import neurograd as ng
from neurograd import xp
from .base import Function


class BatchNormalizer(Function):
    """
    y = var_scaler * (X - mean) / sqrt(var + eps) + mean_scaler
    mean, var, mean_scaler, var_scaler are broadcastable to X and were
    computed with keepdims=True along `axes`.
    """
    name = "BatchNormalizer"

    # ---- single-output fused kernels ----
    @ng.fuse
    def _fw_fused(X, mean, inv_std, var_scaler, mean_scaler):
        return var_scaler * ((X - mean) * inv_std) + mean_scaler  # gamma * x_hat + beta

    @ng.fuse
    def _dvar_scaler_term_fused(gY, x_centered, inv_std):
        # gY * x_hat
        return gY * (x_centered * inv_std)

    @ng.fuse
    def _dvar_term_fused(gY, x_centered, inv_std3, var_scaler):
        # gY * gamma * x_centered * (-1/2) * (var+eps)^(-3/2)
        return gY * (var_scaler * x_centered * (-0.5) * inv_std3)

    @ng.fuse
    def _dmean_term_fused(gY, inv_std, var_scaler):
        # gY * ( -gamma * inv_std )
        return gY * (-(var_scaler * inv_std))

    # ---- Single fused kernel for complete dX computation ----
    @ng.fuse
    def _dX_fused(gY, x_centered, inv_std, var_scaler, dvar_sum, dmean_sum, N):
        # Complete dX = direct_term - correction_terms
        # direct_term = gY * gamma * inv_std
        # correction = (dvar_sum * x_centered * inv_std + dmean_sum) / N
        return gY * (var_scaler * inv_std) - (dvar_sum * x_centered * inv_std + dmean_sum) / N

    def __init__(self, axes, epsilon: float = 1e-5):
        super().__init__()
        self.axes = axes if isinstance(axes, tuple) else (axes,)
        self.epsilon = float(epsilon)

    def forward(self, X: xp.ndarray, mean: xp.ndarray, var: xp.ndarray,
                mean_scaler: xp.ndarray, var_scaler: xp.ndarray) -> xp.ndarray:
        inv_std = xp.asarray(1.0 / xp.sqrt(var + self.epsilon), dtype=xp.float32)
        mean32 = xp.asarray(mean, dtype=xp.float32)
        var_scaler32 = xp.asarray(var_scaler, dtype=xp.float32)
        mean_scaler32 = xp.asarray(mean_scaler, dtype=xp.float32)
        out = BatchNormalizer._fw_fused(X, mean32, inv_std, var_scaler32, mean_scaler32)
        return out.astype(X.dtype, copy=False)

    def backward(self, grad_output: xp.ndarray):
        X, mean, var, mean_scaler, var_scaler = self.parent_tensors
        axes = self.axes

        inv_std  = xp.asarray(1.0 / xp.sqrt(var.data + self.epsilon), dtype=xp.float32)
        x_center = xp.asarray(X.data - mean.data, dtype=xp.float32)
        inv_std3 = inv_std * inv_std * inv_std  # More numerically stable than **3

        # Compute batch size (number of elements being normalized)
        N = 1
        for ax in axes:
            N *= X.data.shape[ax]
        N = float(N)

        # Standard gradients
        dmean_scaler = (xp.sum(grad_output, axis=axes, keepdims=True)
                        if mean_scaler.requires_grad else None)

        dvar_scaler = (xp.sum(BatchNormalizer._dvar_scaler_term_fused(grad_output, x_center, inv_std),
                              axis=axes, keepdims=True)
                       if var_scaler.requires_grad else None)

        dmean = (xp.sum(BatchNormalizer._dmean_term_fused(grad_output, inv_std, xp.asarray(var_scaler.data, dtype=xp.float32)),
                        axis=axes, keepdims=True)
                 if mean.requires_grad else None)

        dvar = (xp.sum(BatchNormalizer._dvar_term_fused(grad_output, x_center, inv_std3, xp.asarray(var_scaler.data, dtype=xp.float32)),
                       axis=axes, keepdims=True)
                if var.requires_grad else None)

        # Complete dX computation in single fused kernel
        if X.requires_grad:
            # First compute the sums needed for corrections
            dvar_sum = xp.sum(BatchNormalizer._dvar_term_fused(grad_output, x_center, inv_std3, xp.asarray(var_scaler.data, dtype=xp.float32)),
                             axis=axes, keepdims=True)
            dmean_sum = xp.sum(BatchNormalizer._dmean_term_fused(grad_output, inv_std, xp.asarray(var_scaler.data, dtype=xp.float32)),
                              axis=axes, keepdims=True)
            
            # Single fused kernel for complete dX
            dX = BatchNormalizer._dX_fused(grad_output, x_center, inv_std, xp.asarray(var_scaler.data, dtype=xp.float32), dvar_sum, dmean_sum, N)
            
            dX = dX.astype(X.data.dtype, copy=False)
        else:
            dX = None

        return dX, dmean, dvar, dmean_scaler, dvar_scaler


def batch_normalize(X, mean, var, mean_scaler, var_scaler, axes, epsilon=1e-5):
    return BatchNormalizer(axes, epsilon)(X, mean, var, mean_scaler, var_scaler)