import neurograd as ng


def test_tensordot_backward_preserves_parent_dtypes():
    xp = ng.xp
    xp.random.seed(0)

    A = ng.Tensor(xp.random.randn(2, 3).astype(xp.float16), requires_grad=True)
    B = ng.Tensor(xp.random.randn(3, 4).astype(xp.float16), requires_grad=True)

    Y = A.tensordot(B, axes=([1], [0]))  # shape (2, 4), dtype fp16
    # Force upstream gradient to be fp32 via an explicit cast before reduction
    loss = Y.cast(xp.float32).sum()
    loss.backward()

    assert A.grad is not None and A.grad.dtype == xp.float16
    assert B.grad is not None and B.grad.dtype == xp.float16


def test_grad_accumulation_no_upcast():
    xp = ng.xp
    xp.random.seed(1)

    p = ng.Tensor(xp.random.randn(5).astype(xp.float16), requires_grad=True)
    # Create two branches that will both contribute to p's grad and cast to fp32 upstream
    y1 = (p * p).cast(xp.float32).sum()
    y2 = (p + 1.0).cast(xp.float32).sum()
    total = y1 + y2
    total.backward()

    assert p.grad is not None and p.grad.dtype == xp.float16


def test_backward_arg_casts_to_output_dtype():
    xp = ng.xp
    # Scalar tensor in fp16
    s = ng.Tensor(xp.array(2.0, dtype=xp.float16), requires_grad=True)
    # Provide a float32 grad; engine should cast to fp16 internally
    s.backward(grad=xp.array(3.0, dtype=xp.float32))
    assert s.grad is not None and s.grad.dtype == xp.float16

