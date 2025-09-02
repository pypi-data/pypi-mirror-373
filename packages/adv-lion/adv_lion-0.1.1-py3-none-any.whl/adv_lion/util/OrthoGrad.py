import torch
from torch import Tensor

def _orthogonalize_gradient(p: Tensor, grad: Tensor) -> Tensor:
    """
    Projects the gradient `grad` to be orthogonal to the parameter `p`,
    and then re-scales the result to have the same norm as the original gradient.
    This method is based on the `OrthoGrad` optimizer from the paper
    "Grokking at the Edge of Numerical Stability" (Prieto et al., 2025):
    (https://arxiv.org/abs/2501.04697)
    It is intended to prevent Naïve Loss Minimization (NLM) by removing the component
    of the gradient that is parallel to the weight vector.
    """
    if grad.is_sparse:
        raise RuntimeError("OrthoGrad logic does not support sparse gradients.")
    original_shape = grad.shape
    original_dtype = grad.dtype
    w = p.view(-1).float()
    g = grad.view(-1).float()
    # Project g onto w: proj_w(g) = (w·g / w·w) * w
    # The small epsilon is for numerical stability.
    w_norm_sq = torch.dot(w, w).add_(1e-30)
    proj = torch.dot(w, g) / w_norm_sq
    # The orthogonal component: g_orth = g - proj_w(g)
    g_orth = g.sub(w, alpha=proj)
    # Rescale g_orth to have the same L2 norm as the original gradient g.
    g_norm = g.norm(2)
    g_orth_norm = g_orth.norm(2).add_(1e-30)
    g_orth_scaled = g_orth * (g_norm / g_orth_norm)
    return g_orth_scaled.view(original_shape).to(original_dtype)