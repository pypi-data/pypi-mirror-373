import torch

from util.Randomized_SVD import _rsvd
from util.OrthoGrad import _orthogonalize_gradient
from util.Effective_Shape import _get_effective_shape
from util.BF16_Stochastic_Rounding import add_stochastic_

class MLorc_CAME(torch.optim.Optimizer):
    """
    Implements a combination of CAME and MLorc algorithms.
    The first moment (momentum) is compressed using the low-rank factorization
    from MLorc, while the adaptive pre-conditioning and confidence-guided
    updates are from CAME.

    This implementation is based on:
    - `CAME: Confidence-guided Adaptive Memory Efficient Optimization` (https://arxiv.org/abs/2307.02047)
    - `MLorc: Momentum Low-rank Compression for Large Language Model Adaptation` (https://arxiv.org/abs/2506.01897)

    Args:
        params (iterable): iterable of parameters to optimize or dicts defining
            parameter groups
        lr (float): learning rate (default: 1e-3)
        betas (tuple[float, float, float]): coefficients for computing running averages of
            update, square gradient, and instability (default: (0.9, 0.999, 0.9999)))
        eps (tuple[float, float]): regularization constants for square gradient
            and instability (default: (1e-30, 1e-16))
        clip_threshold (float): threshold of root-mean-square of
            final gradient update (default: 1.0)
        weight_decay (float): weight decay (L2 penalty) (default: 0)
        rank (int): the rank for the low-rank approximation of the first moment (default: 4).
        oversampling (int): oversampling parameter for Randomized SVD. (default: 0).
        vector_reshape (bool): whether to reshape 1D vectors into 2D
            matrices to apply low-rank compression (default: True).
        stochastic_rounding (bool): whether to use stochastic
            rounding for BF16 parameter updates (default: False).
        use_grams (bool): whether to combine the gradient's direction with the
            update's magnitude (default: False).
    """

    def __init__(
        self,
        params,
        lr: float = 1e-3,
        betas: tuple[float, float, float] = (0.9, 0.999, 0.9999),
        eps: tuple[float, float] = (1e-30, 1e-16),
        clip_threshold: float = 1.0,
        weight_decay: float = 0.0,
        rank: int = 4,
        oversampling: int = 0,
        vector_reshape: bool = True,
        stochastic_rounding: bool = True,
        use_grams: bool = False,
        use_orthograd: bool = False,
    ):
        if not (lr > 0.0):
            raise ValueError(f"Learning-rate should be > 0.0. Got {lr}")
        if not all(0.0 <= beta < 1.0 for beta in betas):
            raise ValueError(f"Betas should be in [0.0, 1.0). Got {betas}")
        if not (rank >= 1):
            raise ValueError(f"Rank should be >= 1. Got {rank}")

        defaults = {
            "lr": lr, "betas": betas, "eps": eps, "clip_threshold": clip_threshold,
            "weight_decay": weight_decay, "rank": rank, "oversampling": oversampling,
            "vector_reshape": vector_reshape, 
        }
        self.stochastic_rounding = stochastic_rounding
        self.use_grams = use_grams
        self.use_orthograd = use_orthograd
        super().__init__(params, defaults)

    @property
    def supports_memory_efficient_fp16(self):
        return True

    @property
    def supports_flat_params(self):
        return False

    def _rms(self, tensor):
        return tensor.norm(2) / (tensor.numel()**0.5)

    def _approx_sq_grad(self, exp_avg_sq_row, exp_avg_sq_col):
        r_factor = (
            (exp_avg_sq_row / exp_avg_sq_row.mean(dim=-1, keepdim=True))
            .rsqrt_()
            .unsqueeze(-1)
        )
        c_factor = exp_avg_sq_col.unsqueeze(-2).rsqrt()
        return torch.mul(r_factor, c_factor)

    @torch.no_grad()
    def step_parameter(self, p: torch.Tensor, group: dict, i: int | None = None):
        if p.grad is None:
            return
        grad = p.grad
        if grad.dtype != torch.float32:
            grad = grad.float()
        if self.use_orthograd:
            grad = _orthogonalize_gradient(p, grad)
        if grad.is_sparse:
            raise RuntimeError("MLorc_CAME does not support sparse gradients.")

        state = self.state[p]

        # State Initialization
        if len(state) == 0:
            state["step"] = 0
            state["RMS"] = 0
            state["factored"] = not (len(p.shape) == 1 and not group["vector_reshape"])
            device, dtype = p.device, torch.float32
            if state["factored"]:
                state["effective_shape"] = _get_effective_shape(p.numel())
                d1, d2 = state["effective_shape"]
                r = group["rank"]

                # MLorc factors for the first moment (m)
                state["mu_m"] = torch.zeros(d1, r, device=device, dtype=dtype)
                state["ms_m"] = torch.zeros(r, device=device, dtype=dtype)
                state["mv_m"] = torch.zeros(r, d2, device=device, dtype=dtype)

                # CAME state for 2nd moment & instability
                grad_shape = state["effective_shape"]
                state["exp_avg_sq_row"] = torch.zeros(grad_shape[:-1], device=device, dtype=dtype)
                state["exp_avg_sq_col"] = torch.zeros(grad_shape[:-2] + grad_shape[-1:], device=device, dtype=dtype)
                state["exp_avg_res_row"] = torch.zeros(grad_shape[:-1], device=device, dtype=dtype)
                state["exp_avg_res_col"] = torch.zeros(grad_shape[:-2] + grad_shape[-1:], device=device, dtype=dtype)
            else:  # Fallback to standard CAME for non-factored tensors
                state["exp_avg"] = torch.zeros_like(grad, device=device, dtype=dtype)
                state["exp_avg_sq"] = torch.zeros_like(grad, device=device, dtype=dtype)

        state["step"] += 1
        state["RMS"] = self._rms(p.data)
        beta1, beta2, beta3 = group["betas"]

        if state["factored"]:
            # --- Factored Tensor Logic (MLorc + CAME) ---
            grad_reshaped = grad.view(state["effective_shape"])

            # 1. CAME: Pre-condition the gradient
            update_sq = (grad_reshaped**2) + group["eps"][0]
            exp_avg_sq_row, exp_avg_sq_col = state["exp_avg_sq_row"], state["exp_avg_sq_col"]
            exp_avg_sq_row.mul_(beta2).add_(update_sq.mean(dim=-1), alpha=1.0 - beta2)
            exp_avg_sq_col.mul_(beta2).add_(update_sq.mean(dim=-2), alpha=1.0 - beta2)

            preconditioned_grad = self._approx_sq_grad(exp_avg_sq_row, exp_avg_sq_col)
            preconditioned_grad.mul_(grad_reshaped)
            preconditioned_grad.div_((self._rms(preconditioned_grad) / group["clip_threshold"]).clamp_(min=1.0))

            # 2. MLorc: Update the first moment (exp_avg)
            mt_prev = state["mu_m"] @ torch.diag(state["ms_m"]) @ state["mv_m"]
            exp_avg = mt_prev.mul_(beta1).add_(preconditioned_grad, alpha=1.0 - beta1)

            # 3. CAME: Confidence-guided update
            res = (preconditioned_grad - exp_avg)**2 + group["eps"][1]
            exp_avg_res_row, exp_avg_res_col = state["exp_avg_res_row"], state["exp_avg_res_col"]
            exp_avg_res_row.mul_(beta3).add_(res.mean(dim=-1), alpha=1.0 - beta3)
            exp_avg_res_col.mul_(beta3).add_(res.mean(dim=-2), alpha=1.0 - beta3)
            
            res_approx = self._approx_sq_grad(exp_avg_res_row, exp_avg_res_col)
            final_update = res_approx.mul_(exp_avg)
            
            final_update = final_update.view(p.shape)
            if self.use_grams:
                final_update = grad.sign() * final_update.abs()
            final_update.mul_(group["lr"])

            # 5. MLorc: Compress and store the new momentum factors
            mu_m_new, ms_m_new, mv_m_new = _rsvd(exp_avg, group['rank'], group['oversampling'])
            state['mu_m'].copy_(mu_m_new)
            state['ms_m'].copy_(ms_m_new)
            state['mv_m'].copy_(mv_m_new)
        else:
            # --- Non-Factored Tensor Logic (Standard CAME) ---
            exp_avg, exp_avg_sq = state["exp_avg"], state["exp_avg_sq"]
            
            update_sq = (grad**2) + group["eps"][0]
            exp_avg_sq.mul_(beta2).add_(update_sq, alpha=1.0 - beta2)
            preconditioned_grad = exp_avg_sq.rsqrt().mul_(grad)
            
            preconditioned_grad.div_((self._rms(preconditioned_grad) / group["clip_threshold"]).clamp_(min=1.0))
            
            exp_avg.mul_(beta1).add_(preconditioned_grad, alpha=1 - beta1)
            
            final_update = exp_avg.clone() # CAME uses raw momentum for non-factored tensors

            if self.use_grams:
                final_update = grad.sign() * final_update.abs()
                    
            final_update.mul_(group["lr"])

        if group["weight_decay"] != 0:
            if p.dtype == torch.bfloat16 and self.stochastic_rounding:
                add_stochastic_(p.data, p.data, alpha=-group["weight_decay"] * group["lr"])
            else:
                p.data.add_(p.data, alpha=-group["weight_decay"] * group["lr"])

        if p.dtype == torch.bfloat16 and self.stochastic_rounding:
            add_stochastic_(p.data, -final_update)
        else:
            p.data.add_(-final_update)

    @torch.no_grad()
    def step(self, closure=None):
        """Performs a single optimization step."""
        loss = None
        if closure is not None:
            with torch.enable_grad():
                loss = closure()

        for group in self.param_groups:
            for i, p in enumerate(group["params"]):
                self.step_parameter(p, group, i)

        return loss