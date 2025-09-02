import torch

from typing import Tuple, Optional

from ..util.OrthoGrad import _orthogonalize_gradient
from ..util.bf16_stochastic_rounding import add_stochastic_

class Lion(torch.optim.Optimizer):
    """
    Implements The Lion update rule (https://arxiv.org/abs/2302.06675).

    Args:
        params (iterable): iterable of parameters to optimize or dicts defining
            parameter groups.
        lr (float, optional): learning rate (default: 1e-6).
        betas (Tuple[float, float], optional): coefficients for computing
            running averages of the update (default: (0.9, 0.99)).
        weight_decay (float, optional): weight decay (L2 penalty) (default: 0.0).
        stochastic_rounding (bool, optional): whether to use stochastic
            rounding for BF16 parameter updates (default: False).
        use_orthograd (bool): whether to use OrthoGrad.  (default: False)
        use_cautious (bool): whether to use cautious variant.  (default: False)
        use_variance_reduction (bool): whether to use the variance reduction technique
            from "Convergence Analysis of the Lion Optimizer" (arXiv:2508.12327v1). (default: False).
    """

    def __init__(
        self,
        params,
        lr: float = 1e-6,
        betas: Tuple[float, float] = (0.9, 0.99),
        weight_decay: float = 0.0,
        rank: int = 4,
        oversampling: int = 0,
        vector_reshape: bool = True,
        stochastic_rounding: bool = True,
        use_orthograd: bool = False,
        use_cautious: bool = False,
        use_variance_reduction: bool = False,
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
            "rank": rank, "oversampling": oversampling, "vector_reshape": vector_reshape,
            "use_orthograd": use_orthograd,
        }
        self.stochastic_rounding = stochastic_rounding
        self.use_cautious = use_cautious
        self.use_variance_reduction = use_variance_reduction
        super().__init__(params, defaults)

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
            dtype = p.dtype
            state['exp_avg'] = torch.zeros_like(p, device=p.device, dtype=dtype)
            if self.use_variance_reduction:
                state['prev_grad'] = torch.zeros_like(p, device=p.device, dtype=dtype)

        state['step'] += 1
        beta1, beta2 = group["betas"]
        lr = group['lr']

        exp_avg = state["exp_avg"]

        signed_update = exp_avg.clone().mul_(beta1).add_(grad, alpha=(1-beta1)).sign_()

        if self.use_cautious:
            mask = (signed_update * grad > 0).to(grad.dtype)
            mask.div_(mask.mean().clamp_(min=1e-3))
            signed_update.mul_(mask)
            del mask
        signed_update.mul_(lr)

        if group["weight_decay"] != 0:
            if p.dtype == torch.bfloat16 and self.stochastic_rounding:
                add_stochastic_(p.data, p.data,
                                alpha=-group["weight_decay"] * lr)
            else:
                p.data.add_(
                    p.data, alpha=-group["weight_decay"] * lr
                )

        if p.dtype == torch.bfloat16 and self.stochastic_rounding:
            add_stochastic_(p.data, -signed_update)
        else:
            p.data.add_(-signed_update)

        del signed_update

        # Update momentum m_t
        if self.use_variance_reduction:
            vr_term = grad - state['prev_grad']
            exp_avg_update = exp_avg.mul(beta2).add(grad, alpha=1-beta2).add(vr_term, alpha=beta2)
            state['prev_grad'].copy_(grad)
        else:
            exp_avg_update = exp_avg.mul(beta2).add(grad, alpha=1-beta2)
        state['exp_avg'].copy_(exp_avg_update)

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

        return loss