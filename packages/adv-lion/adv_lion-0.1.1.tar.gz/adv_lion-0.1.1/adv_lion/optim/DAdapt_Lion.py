import torch

from typing import Tuple, Optional
import torch.distributed as dist

import logging


from ..util.OrthoGrad import _orthogonalize_gradient
from ..util.bf16_stochastic_rounding import add_stochastic_

class DAdapt_Lion(torch.optim.Optimizer):
    """
    Implements The Lion update rule (https://arxiv.org/abs/2302.06675) with D-Adaptation (https://arxiv.org/abs/2301.07733).

    Args:
        params (iterable): iterable of parameters to optimize or dicts defining
            parameter groups.
        lr (float, optional): learning rate (default: 1).
        betas (Tuple[float, float], optional): coefficients for computing
            running averages of the update (default: (0.9, 0.99)).
        weight_decay (float, optional): weight decay (L2 penalty) (default: 0.0).
        stochastic_rounding (bool, optional): whether to use stochastic
            rounding for BF16 parameter updates (default: False).
        use_orthograd (bool): whether to use OrthoGrad.  (default: False)
        use_variance_reduction (bool): whether to use the variance reduction technique
            from "Convergence Analysis of the Lion Optimizer" (arXiv:2508.12327v1). (default: False).
        use_cautious (bool): whether to use cautious variant.  (default: False)
        d0 (float, optional): Initial D estimate for D-adaptation (default 1e-6).
        slice_p (int, optional): Reduce memory usage by calculating LR adaptation statistics
            on only every p-th entry of each tensor. For values greater than 1 this is
            an approximation. (default: 11).
        log_every (int, optional): Log D-adaptation statistics every k steps.
            0 means no logging (default: 0).
        fsdp_in_use (bool, optional): Set to True if using FSDP, for correct
            distributed aggregation (default: False).
    """

    def __init__(
        self,
        params,
        lr: float = 1,
        betas: Tuple[float, float] = (0.9, 0.99),
        weight_decay: float = 0.0,
        stochastic_rounding: bool = True,
        use_orthograd: bool = False,
        use_cautious: bool = False,
        use_variance_reduction: bool = False,
        # D-Adaptation parameters
        d0: float = 1e-6,
        slice_p: int = 11,
        log_every: int = 0,
        fsdp_in_use: bool = False,
    ):
        if not lr > 0.0:
            raise ValueError(f"Learning rate must be > 0.0, but got {lr}")
        if not all(0.0 <= beta <= 1.0 for beta in betas):
            raise ValueError(f"Betas should be in [0.0, 1.0], but got {betas}")
        if not weight_decay >= 0.0:
            raise ValueError(f"Weight decay must be >= 0.0, but got {weight_decay}")
        if use_variance_reduction and use_cautious:
            print("Warning: Using both 'use_variance_reduction' and 'use_cautious' is not recommended and may lead to unintended effects.")

        defaults = {
            "lr": lr, "betas": betas, "weight_decay": weight_decay,
            "use_orthograd": use_orthograd,
            # D-Adaptation settings
            "d": d0, "slice_p": slice_p, "k": 0, "log_every": log_every,
            "numerator_weighted": 0.0, "fsdp_in_use": fsdp_in_use,
        }
        self.stochastic_rounding = stochastic_rounding
        self.use_cautious = use_cautious
        self.use_variance_reduction = use_variance_reduction
        super().__init__(params, defaults)

        # Global state for accumulating metrics across parameter updates within a single step.
        self.global_state = {"numerator_acum": 0.0, "sk_l1": 0.0}

    @property
    def supports_fused_back_pass(self) -> bool:
        return True

    @property
    def supports_memory_efficient_fp16(self) -> bool:
        return True

    @property
    def supports_flat_params(self) -> bool:
        return False

    @torch.no_grad()
    def step_parameter(self, p: torch.Tensor, group: dict, i: Optional[int] = None):
        """Performs a single optimization step on a single parameter."""
        if p.grad is None:
            return
        grad = p.grad
        if group["use_orthograd"]:
            grad = _orthogonalize_gradient(p, grad)
        state = self.state[p]

        # State Initialization
        if len(state) == 0:
            state['step'] = 0
            slice_p = group['slice_p']
            # D-Adaptation state
            state['s'] = torch.zeros_like(p.flatten()[::slice_p], device=p.device) if slice_p > 1 else torch.zeros_like(p)
            # momentum state
            state['exp_avg'] = torch.zeros_like(p, device=p.device, dtype=p.dtype)
            # variance state
            if group['use_variance_reduction']:
                state['prev_grad'] = torch.zeros_like(p, device=p.device, dtype=p.dtype)

        state['step'] += 1
        beta1, beta2 = group["betas"]
        sqrt_beta2 = beta2 ** 0.5
        dlr = group['d'] * group['lr']

        s = state['s']
        signed_update = None

        exp_avg = state["exp_avg"]

        signed_update = exp_avg.clone().mul_(beta1).add_(grad, alpha=(1-beta1)).sign_()

        if self.use_cautious:
            mask = (signed_update * grad > 0).to(grad.dtype)
            mask.div_(mask.mean().clamp_(min=1e-3))
            signed_update.mul_(mask)
            del mask
        update_for_param = signed_update.mul(dlr)

        # Update momentum m_t
        if group['use_variance_reduction']:
            vr_term = grad - state['prev_grad']
            exp_avg_update = exp_avg.mul(beta2).add(grad, alpha=dlr * (1-beta2)).add(vr_term, alpha=beta2)
            state['prev_grad'].copy_(grad)
        else:
            exp_avg_update = exp_avg.mul(beta2).add(grad, alpha=dlr * (1-beta2))
        state['exp_avg'].copy_(exp_avg_update)

        if group["weight_decay"] != 0:
            p.data.add_(p.data, alpha=-group["weight_decay"] * dlr)

        if p.dtype == torch.bfloat16 and self.stochastic_rounding:
            add_stochastic_(p.data, -update_for_param)
        else:
            p.data.add_(-update_for_param)

        del update_for_param

        # --- D-Adaptation Metric Accumulation ---
        # This part populates the global state for the final d-update in step()
        slice_p = group['slice_p']
        if slice_p > 1: # slicing path, for memory efficiency
            sliced_signed_update = signed_update.flatten()[::slice_p]
            numerator_contrib = dlr * torch.dot(sliced_signed_update, s)
            s.mul_(sqrt_beta2).add_(sliced_signed_update, alpha=(1 - sqrt_beta2) * dlr)
            sk_l1_contrib = s.abs().sum()
        else: # Original, non-slicing path
            numerator_contrib = dlr * torch.dot(signed_update.view(-1), s.view(-1))
            s.mul_(sqrt_beta2).add_(signed_update.view_as(s), alpha=(1 - sqrt_beta2) * dlr)
            sk_l1_contrib = s.abs().sum()
        self.global_state["numerator_acum"] += numerator_contrib.item()
        self.global_state["sk_l1"] += sk_l1_contrib.item()

    @torch.no_grad()
    def step(self, closure: Optional[callable] = None):
        """Performs a single optimization step."""
        loss = None
        if closure is not None:
            with torch.enable_grad():
                loss = closure()

        for group in self.param_groups:
            for i, p in enumerate(group["params"]):
                if p.grad is not None:
                    self.step_parameter(p, group, i)

        # --- D-Adaptation Finalization Step ---
        # This logic runs after all parameter updates for the step are complete.
        g_ref = self.param_groups[0]
        fsdp_in_use = g_ref['fsdp_in_use']
        numerator_weighted = g_ref['numerator_weighted']
        d = g_ref['d']
        lr = g_ref['lr']
        beta2 = g_ref['betas'][1]
        sqrt_beta2 = beta2 ** 0.5
        log_every = g_ref['log_every']
        k = g_ref['k']

        numerator_acum = self.global_state["numerator_acum"]
        sk_l1 = self.global_state["sk_l1"]

        if sk_l1 == 0:  # If no gradients were processed, skip d-adaptation update
            self.global_state = {"numerator_acum": 0.0, "sk_l1": 0.0}
            return loss

        if fsdp_in_use: # Aggregate numerator and sk_l1 across all ranks
            dist_tensor = torch.tensor([numerator_acum, sk_l1], device=self.param_groups[0]['params'][0].device)
            dist.all_reduce(dist_tensor, op=dist.ReduceOp.SUM)
            global_numerator_acum = dist_tensor[0].item()
            global_sk_l1 = dist_tensor[1].item()
        else:
            global_numerator_acum = numerator_acum
            global_sk_l1 = sk_l1

        # Update weighted numerator
        global_numerator_weighted = sqrt_beta2 * numerator_weighted + (1 - sqrt_beta2) * global_numerator_acum

        d_hat = 0.0
        if global_sk_l1 > 0:
            d_hat = global_numerator_weighted / ((1 - sqrt_beta2) * global_sk_l1)

        if lr > 0.0:
            d = max(d, d_hat)

        if log_every > 0 and k % log_every == 0:
            logging.info(f"lr: {lr} d: {d:.4e} d_hat: {d_hat:.4e} dlr: {d*lr:.4e} sk_l1={global_sk_l1:1.1e}")

        # Update shared state in all param groups
        for group in self.param_groups:
            group['d'] = d
            group['numerator_weighted'] = global_numerator_weighted
            group['k'] += 1

        # Reset global state for the next optimization step
        self.global_state = {"numerator_acum": 0.0, "sk_l1": 0.0}

        return loss