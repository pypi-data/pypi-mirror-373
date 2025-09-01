
from typing import Set, Dict, List, Any, Callable
import operator
import warnings
import numpy as np


_IGNORED_OPS: Set[str] = {
    "aten::Int",
    "aten::ScalarImplicit",
    "aten::__and__",
    "aten::arange",
    "aten::bitwise_not",
    "aten::cat",
    "aten::chunk",
    "aten::clamp",
    "aten::clamp_",
    "aten::constant_pad_nd",
    "aten::contiguous",
    "aten::copy_",
    "aten::detach",
    "aten::dropout",
    "aten::empty",
    "aten::eq",
    "aten::expand",
    "aten::flatten",
    "aten::full",
    "aten::full_like",
    "aten::gather",
    "aten::ge",
    "aten::gt",
    "aten::index",
    "aten::index_put_",
    "aten::masked_fill",
    "aten::max",
    "aten::narrow",
    "aten::new_empty",
    "aten::new_full",
    "aten::new_zeros",
    "aten::nonzero",
    "aten::ones",
    "aten::permute",
    "aten::relu",
    "aten::relu_",
    "aten::reshape",
    "aten::roll",
    "aten::select",
    "aten::size",
    "aten::slice",
    "aten::split",
    "aten::split_with_sizes",
    "aten::squeeze",
    "aten::stack",
    "aten::t",
    "aten::to",
    "aten::transpose",
    "aten::type_as",
    "aten::unbind",
    "aten::unsqueeze",
    "aten::unsqueeze_",
    "aten::view",
    "aten::zeros",
    "aten::zeros_like",

    # add by kunlong
    "aten::scatter.src",
    "aten::repeat",
    "aten::clone",
    "aten::slice.Tensor",
    "aten::select.int",
    "aten::squeeze.dim",
    "aten::transpose.int",
    "aten::_to_copy",
    "aten::_unsafe_view",
    "aten::copy",
    "aten::new_empty_strided",
    "aten::scalar_tensor",
    "aten::select_backward",
    "aten::slice_backward",
    'aten::linspace',
    'aten::bernoulli.p',
    'aten::randn',
    'aten::lift_fresh_copy',
    'aten::unbind.int',
    'aten::max_pool2d_with_indices_backward',

    # logical operation add by zkl
    'aten::sort',
    'aten::max.dim',
    'aten::logical_and',
    'aten::le.Scalar',
    'aten::where.self',
    'aten::ge.Scalar',
    'aten::threshold_backward',
    'aten::max_pool2d_with_indices',
}

_PYTHON_IGNORED_OPS: Set = {
    operator.getitem,
    operator.setitem,
    operator.delitem,
    operator.itemgetter,
    operator.length_hint,

    operator.attrgetter,
    operator.methodcaller,

    operator.not_,
    operator.truth,
    operator.is_,
    operator.is_not,

    operator.index,
    operator.concat,
    operator.contains,
    operator.countOf,
    operator.delitem,
    operator.setitem,
}

def conv_ops_counter(inputs:List[Any]) -> int:
    """
    Count the number of operations for a convolution layer.
    Args:
        inputs (List[Any]): List of inputs to the convolution layer.
            Expected to contain:
            - input tensor (N, C_in, H_in, W_in)
            - weight tensor (C_out, C_in/groups, kH, kW)
            - bias tensor (C_out,) or None
            - stride (tuple)
            - padding (tuple)
            - dilation (tuple)
            - transposed (bool)
            - output_padding (tuple)
            - groups (int)
    Returns:
        int: Number of operations for the convolution layer.
    """
    input_tensor = inputs[0]
    weight_tensor = inputs[1]
    bias_tensor = inputs[2]
    stride = inputs[3]
    padding = inputs[4]
    dilation = inputs[5]
    transposed = inputs[6]
    output_padding = inputs[7]
    groups = inputs[8]

    # 输入张量形状
    N, C_in, H_in, W_in = input_tensor.meta['val'].shape
    C_out, _, kH, kW = weight_tensor.meta['val'].shape
    strideH, strideW = stride
    padH, padW = padding
    dilH, dilW = dilation
    out_padH, out_padW = output_padding

    # 输出尺寸计算
    if not transposed: 
        # Actual kernel size: $$(K-1)(D-1) + K = D(K-1) + 1$$
        # Out size: $$(H + 2p - (D(K-1)+1)) // S + 1$$
        H_out = (H_in + 2*padH - dilH*(kH-1) -1)//strideH + 1
        W_out = (W_in + 2*padW - dilW*(kW-1) -1)//strideW + 1
    else:
        # 转置卷积公式
        warnings.warn("The caculational operation of Transposed convolution isn't checked!!!")
        H_out = (H_in-1)*strideH - 2*padH + (2-dilH)*kH + dilH - 1
        W_out = (W_in-1)*strideW - 2*padW + (2-dilW)*kW + dilW - 1

    # 每个输出元素的乘加操作
    flops_per_instance = 2 * (C_in // groups) * kH * kW - 1
    total_flops = N * H_out * W_out * C_out * flops_per_instance

    # bias 加法 FLOPs
    if bias_tensor is not None:
        total_flops += N * H_out * W_out * C_out  # 每个输出元素加一次 bias
    return total_flops

def div_tesnor_ops_counter(inputs: List[Any]) -> int:
    try:
        mat1_shape = np.array(inputs[0].meta['val'].shape, dtype=np.int64)
    except:
        mat1_shape = np.array([1], dtype=np.int64)

    try:
        mat2_shape = np.array(inputs[1].meta['val'].shape, dtype=np.int64)
    except:
        mat2_shape = np.array([1], dtype=np.int64)
    
    l =  max(len(mat1_shape), len(mat2_shape))
    shape_store = np.zeros([2, l], np.int64) 
    shape_store[0, l-len(mat1_shape):] = mat1_shape
    shape_store[1, l-len(mat2_shape):] = mat2_shape
    
    flops = shape_store.max(axis=0).prod()

    return flops

def addmm_ops_counter(inputs: List[Any]) -> int:
    bias_shape = inputs[0].meta['val'].shape
    mat1_shape = inputs[1].meta['val'].shape
    mat2_shape = inputs[2].meta['val'].shape
    assert mat2_shape[-1] == bias_shape[0]
    flops = mm_ops_counter(inputs[1:]) + mat1_shape[0] * mat2_shape[1]

    return flops

def sum_dim_IntList_ops_counter(inputs: List[Any]) -> int:
    input_shape = list(inputs[0].meta['val'].shape)
    dims = inputs[1]
    K = []
    for dim in dims:
        K.append(input_shape[dim])
        input_shape[dim] = 1
    
    K = np.array(K, dtype=np.int64).prod()

    flops = np.array(input_shape, dtype=np.int64).prod() * (K - 1)

    return flops

def sigmoid_ops_counter(inputs: List[Any]) -> int:
    """
    $$ sigmoid(x) = \frac{1}{1 + e^{-x}} $$

    """
    try:
        tensor_shape = np.array(inputs[0].meta['val'].shape, dtype=np.int64)
    except:
        tensor_shape = np.array([1], dtype=np.int64)
    
    flops = 3 * tensor_shape.prod()

    return flops

def _soft_max_ops_counter(inputs: List[Any]) -> int:
    """
    N = np.array(Shape).prod()
    M = N / Shape[dim]
    FLOPs:
    # minus_max_value (for overflow) = N (ignore in theory)
    exp() = N
    add = N - M
    div = N
    flops = minus_max_value + exp() + add + div
    """
    tensor_shape = np.array(inputs[0].meta['val'].shape, dtype=np.int64)
    dim = inputs[1]
    N = np.array(tensor_shape).prod()
    tensor_shape[dim] = 1
    M = tensor_shape.prod()
    flops = 3 * N - M 

    return flops


def mm_ops_counter(inputs: List[Any]) -> int:
    M, K = inputs[0].meta['val'].shape
    _, N = inputs[1].meta['val'].shape
    assert K == _
    flops = M * N * (2*K - 1)

    return flops

def remainder_Scalar_ops_counter(inputs: List[Any]) -> int:
    try:
        tensor_shape = np.array(inputs[0].meta['val'].shape, dtype=np.int64)
    except:
        tensor_shape = np.array([1], dtype=np.int64)
    flops = tensor_shape.prod()

    return flops

def bmm_ops_counter(inputs: List[Any]) -> int:
    mat1_shape = inputs[0].meta['val'].shape
    mat2_shape = inputs[1].meta['val'].shape
    B, M, K = mat1_shape
    _, _, N = mat2_shape

    flops = B * M * N * (2*K - 1)

    return flops

def add_Tensor_ops_counter(inputs: List[Any]) -> int:
    a = inputs[0]
    b = inputs[1]
    try:
        a_shape = np.array(a.meta['val'].shape, np.int64)
    except:
        a_shape = np.array([1], dtype=np.int64)

    try:
        b_shape = np.array(b.meta['val'].shape, np.int64)
    except:
        b_shape = np.array([1], dtype=np.int64)
    if (len(a_shape) <= 1):
        flops = b_shape.prod()
    elif (len(b_shape) <= 1):
        flops = a_shape.prod()
    else:
        l =  max(len(a_shape), len(b_shape))
        shape_store = np.zeros([2, l], np.int64) 
        shape_store[0, l-len(a_shape):] = a_shape
        shape_store[1, l-len(b_shape):] = b_shape
        
        flops = shape_store.max(axis=0).prod()
    
    return flops
        


def native_layer_norm_ops_conuter(inputs: List[Any]) -> int:
    """
    N, L, C: Batch size, Sequence length, Feature channel
    Flops:
    mean = $$ N \times L \times C $$
    std = $$ N \times L \times [C \times 2 + (C-1 + 2))] = N \times L \times C \times 3 + N \times L $$
    normal & scale & shift = $$ N \times L \times C \times 4 $$
    ALL: $$ N \times L \times C \times 8 + N \times C $$
    """
    input_tensor = inputs[0]
    normalized_shape = inputs[1]
    assert len(normalized_shape) == 1, "Only support 'normalized_shape=2 !!!'"
    N, L, C = input_tensor.meta['val'].shape

    flops = N * C * L * 8 + N * C
    return flops

def mul_ops_counter(inputs: List[Any]) -> int:
    try:
        mat1_shape = list(inputs[0].meta['val'].shape)
    except:
        mat1_shape = [1]
    
    try:
        mat2_shape = list(inputs[1].meta['val'].shape)
    except:
        mat2_shape = [1]
    
    assert (mat1_shape[-1] == mat2_shape[-1]) or (mat1_shape[-1] == 1) or (mat2_shape[-1] == 1)

    mat1_shape = np.array(mat1_shape, dtype=np.int64)
    mat2_shape = np.array(mat2_shape, dtype=np.int64)

    l =  max(len(mat1_shape), len(mat2_shape))
    shape_store = np.zeros([2, l], dtype=np.int64) 
    shape_store[0, l-len(mat1_shape):] = mat1_shape
    shape_store[1, l-len(mat2_shape):] = mat2_shape

    flops = shape_store.max(axis=0).prod()

    return flops


def mean_dim_ops_counter(inputs: List[Any]) -> int:
    tensor_shape = np.array(inputs[0].meta['val'].shape, dtype=np.int64)
    flops = tensor_shape.prod()

    return flops

def gelu_ops_counter(inputs: List[Any]) -> int:
    """
    $$\text{GELU}(x) \approx 0.5 \cdot x \cdot \left(1 + 
    \tanh\left( \sqrt{\frac{2}{\pi}} \cdot 
    \left( x + 0.044715 \cdot x^3 \right) \right) \right)$$
    $$FLOPs(tanh) \approx 1 $$
    """
    tensor_shape = np.array(inputs[0].meta['val'].shape, dtype=np.int64)
    flops = 8 * tensor_shape.prod()

    return flops

def _native_batch_norm_legit_functional_ops_counter(inputs: List[Any]) -> int:
    """  Batch Normalization
  
    $$ y = \gamma \cdot \frac{x-\mu_{B}}{\sqrt{\delta^2_{B} + \epsilon}} 
    + \beta $$
    
    $$N, C, H, W$$ = Batch size, Channel, Height, Width 
    Train Mode:
    $$ FLOPs(\mu_B) = (N \times H \times W) \times C $$
    $$ FLOPs(\delta^2_{B}) = (N \times H \times W \times 3) \times C $$


    $$ FLOPs(\frac{x-\mu_{B}}{\sqrt{\delta^2_{B}}}) = 
    (N \times H \times W \times 2) \times C$$

    $$ FLOPs(\gamma \cdot () + \beta) = 
    (N \times H \times W \times 2) \times C $$

    Train FLOPs = $$ N \times H \times W \times C \times 8 $$
    ====================================================
    Eval Mode:
    $$ FLOPs(\mu_B) = 0 $$
    $$ FLOPs(\delta^2_{B}) = 0 $$
    Eval FLOPs =  $$ N \times H \times W \times C \times 4 $$
    """
    tensor_shape = np.array(inputs[0].meta['val'].shape, dtype=np.int64)
    train = inputs[5]

    flops = tensor_shape.prod() * (8 if train else 4)

    return flops

def remainder_Tensor_ops_counter(inputs: List[Any]) -> int:
    try:
        mat1_shape = np.array(inputs[0].meta['val'].shape, dtype=np.int64)
    except:
        mat1_shape = np.array([1], dtype=np.int64)

    try:
        mat2_shape = np.array(inputs[1].meta['val'].shape, dtype=np.int64)
    except:
        mat2_shape = np.array([1], dtype=np.int64)

    l = max(len(mat1_shape), len(mat2_shape))
    shape = np.zeros([2, l], dtype=np.int64)
    shape[0, l-len(mat1_shape):] = mat1_shape
    shape[1, l-len(mat2_shape):] = mat2_shape
    
    flops = shape.max(axis=0).prod()

    return flops

def floor_ops_counter(inputs: List[Any]) -> int:
    raise NotImplementedError

def floor_divide_ops_counter(inputs: List[Any]) -> int:
    try:
        mat1_shape = np.array(inputs[0].meta['val'].shape, dtype=np.int64)
    except:
        mat1_shape = np.array([1], dtype=np.int64)

    try:
        mat2_shape = np.array(inputs[1].meta['val'].shape, dtype=np.int64)
    except:
        mat2_shape = np.array([1], dtype=np.int64)

    l = max(len(mat1_shape), len(mat2_shape))
    shape = np.zeros([2, l], dtype=np.int64)
    shape[0, l-len(mat1_shape):] = mat1_shape
    shape[1, l-len(mat2_shape):] = mat2_shape
    
    flops = shape.max(axis=0).prod()

    return flops

def scatter_add_ops_counter(inputs: List[Any]) -> int:
    src_shape = np.array(inputs[3].meta['val'].shape, dtype=np.int64)
    index_shape = np.array(inputs[2].meta['val'].shape, dtype=np.int64)
    assert (src_shape == index_shape).all()
    flops = src_shape.prod()

    return flops 

def gelu_backward_ops_counter(inputs: List[Any]) -> int:
    """
    $$\text{GELU}(x) \approx 0.5 \cdot x \cdot \left(1 + 
    \tanh\left( \sqrt{\frac{2}{\pi}} \cdot 
    \left( x + 0.044715 \cdot x^3 \right) \right) \right)$$
    
    $$ a = \sqrt{\frac{2}{\pi}}, b=0.044715, c=0.5 , z = a \cdot (x + b \cdot x^3) $$

    $$ GELU(x) \approx c \cdot x \cdot + x \cdot tanh(z) $$


    $$ \frac{dGELU(x)}{dx} \approx c + tanh(z) + x \cdot (1 - tanh^2{(z)}) \cdot a \cdot (1 + b \cdot 3 \cdot x^2)$$

    $$ FLOPs(tanh) \approx 1 $$
    """
    grad_output_shape = np.array(inputs[0].meta['val'].shape, dtype=np.int64)

    flops = grad_output_shape.prod() * 17

    return flops

def convolution_backward_ops_counter(inputs: List[Any]) -> int:
    """
    NOTE: !!! Only support Conv2d!!!
    0 grad_output $$ [B, C_{out}, H_{out}, W_{out}] $$
    1 input $$ [B, C_{in}, H_{in}, W_{in}] $$
    2 weight $$ [C_{out}, C_{in}/groups, K_h, K_w] $$
    3 bias_size ,[0] mean bias = False
    4 stride
    5 padding
    6 dilation
    7 transposed
    8 output_padding (for ConvTranspose2d)
    9 groups
    10 needs_grad: [needs_input_grad, needs_weight_grad, needs_bias_grads]
    """
    grad_output_shape = np.array(inputs[0].meta['val'].shape, dtype=np.int64)
    input_shape = np.array(inputs[1].meta['val'].shape, dtype=np.int64)
    weight_shape = np.array(inputs[2].meta['val'].shape, dtype=np.int64)
    assert len(input_shape) == 4, "Only support Conv2d!!!"
    
    C_out = weight_shape[0]
    
    groups = inputs[9]

    needs_grad = inputs[10]
    flops = 0
    if needs_grad[2]: # bias $$ FLOPs(\frac{dz}{db} = \frac{dz}{dy} \cdot \frac{dy}{db}) $$

                      # $$ FLOPS = B \times H_{out} \times W_{out} \times C_{out} - C_{out}$$
        flops = flops + grad_output_shape.prod() - C_out

    if needs_grad[1]: # weight $$ FLOPs(\frac{dz}{dw}=\frac{dz}{dy} \cdot \frac{dy}{dw}) $$

                      # $$ FLOPs = B \times H_{out} \times W_{out} \times C_{out} \times C_{in}/groups \times K_h \times K_w \times 2 - $$
                      # $$ C_{in}/groups \times K_h \times K_w \times C_{out} $$
        flops = flops + grad_output_shape.prod() * weight_shape[1:].prod() * 2 - weight_shape.prod()

    if needs_grad[0]: # input $$ FLOPs(\frac{dz}{dx} = \frac{dz}{dy} \cdot \frac{dy}{dx}) $$ Here, we ignore the addition operation between overlapped inputs.

                      # $$ FLOPs \approx B \times H_{out} \times W_{out} \times [C_{out} \times C_{in}/groups \times K_h \times K_w *2 - $$
                      # $$ C_{in}/groups \times K_h \times K_w] $$

        flops = flops + grad_output_shape.prod() * weight_shape[1:].prod() * 2 - \
                weight_shape[1:].prod() * groups * grad_output_shape[0] * grad_output_shape[2:].prod()
    return flops

def native_layer_norm_backward_ops_counter(inputs: List[Any]) -> int:
    """
    0 grad_out
    1 input
    2 normalized_shape
    3 gamma
    4 beta
    5 save_mean
    6 save_var
    7 needs_grad: [grad_input, grad_gamma, grad_beta]
    This can refer to Batch Normalization(def native_batch_norm_backward_ops_counter()).
    """
    grad_out_shape = np.array(inputs[0].meta['val'].shape, dtype=np.int64)
    B, L, C = grad_out_shape 
    needs_grad = inputs[7]

    flops = 0
    if needs_grad[2]: # $$ \beta $$
        flops = flops + B * L * (C - 1)

    if needs_grad[1]: # $$ \gamma $$
        flops = flops + B * L * C * 2 - B * L

    if needs_grad[0]: # input
        flops = flops + B * L * C * 5

    return flops

def native_batch_norm_backward_ops_counter(inputs: List[Any]) -> int:
    """
    0 grad_output
    1 intput
    2 gamma
    3 running_mean
    4 running_var
    5 save_mean
    6 save_var
    7 train
    8 eps
    9 needs_grad: [grad_input, grad_gamma, grad_beta]

    $$ y = \gamma \cdot \hat{x} + \beta , \hat{x} = \frac{x-\mu_{B}}{\sqrt{\delta^2_{B} + \epsilon}}$$
    """
    output_shape = np.array(inputs[0].meta['val'].shape, dtype=np.int64)
    B, C, H, W = output_shape
    need_grad = inputs[9]

    assert len(output_shape) == 4, "Only support 2d Batch Normal!!!"

    flops = 0
    if need_grad[2]: # $$ \beta, FLOPs(\frac{dz}{d\beta} = \frac{dz}{dy} \cdot \frac{dy}{d\beta} = \frac{dz}{dy} \cdot 1) $$

                     # $$ FLOPs = C \times (B \times H \times W -1) $$
        flops = flops + C * (B * H * W -1)
    
    if need_grad[1]: # $$ \gamma, FLOPs(\frac{dz}{d\gamma} = \frac{dz}{dy} \cdot \frac{dy}{d\gamma} = \frac{dz}{dy} \cdot \hat{x})$$

                     # $$ FLOPs = C \times B \times H \times W \times 2 - C $$ 
        flops = flops + C * B * H * W * 2 - C
    
    if need_grad[0]: # input $$ x, FLOPs(\frac{dz}{dx} = \frac{dz}{dy} \cdot \frac{dy}{dx} = \frac{dz}{dy} \cdot \gamma \frac{1}{\sqrt{\delta^2_{B} + \epsilon}}) $$
        
                     # $$ FLOPs = C \times B \times H \times W \times 5 $$
        flops = flops + C * B * H * W * 5

    return flops   

def _softmax_backward_data_ops_counter(inputs: List[Any]) -> int:
    """
    0 grad_output
    1 output
    2 dim
    3

    $$ y_i = \frac{e^{x_i}}{\sum_{j=1} e^{x_j}} $$  
    $$ \frac{dy_i}{dx_k} = 
    \left\{ 
    \begin{aligned}
        (y_k - y_k^2), i = k \\
        (-y_k \cdot y_i), i \neq k
    \end{aligned}
    \right. $$
    $$ z  = f(y_1, ..., y_n)$$
    $$ \frac{dz}{dx_k} = \sum_{i=1}^n \frac{dz}{dy_i} \cdot \frac{dy_i}{dx_k} = 
       y_k \cdot (\frac{dz}{dy_k} - \sum_{i=1}^n \frac{dz}{dy_i} \cdot y_i)
    $$
    """
    grad_output_shape = np.array(inputs[0].meta['val'].shape, dtype=np.int64)
    dim = inputs[2]
    C = grad_output_shape[dim]
    grad_output_shape[dim] = 1
    flops =  grad_output_shape.prod() * (4 * C - 1)

    return flops


def sigmoid_backward_ops_counter(inputs: List[Any]) -> int:
    """
    $$ \delta(x) = \frac{1}{1 + e^{-x}} $$

    $$ \frac{d\delta(x)}{dx} = \delta(x) \cdot (1 - \delta(x))$$


    """
    output_shape = np.array(inputs[1].meta['val'].shape, dtype=np.int64)
    flops = output_shape.prod()

    return flops

def div_Scalar_ops_counter(inputs: List[Any]) -> int:
    input_shape = np.array(inputs[0].meta['val'].shape, dtype=np.int64)
    flops= input_shape.prod()

    return flops

_SUPPORTED_OPS: Dict[str, Callable] = {
    "aten::convolution": conv_ops_counter,
    'aten::div.Tensor': div_tesnor_ops_counter,
    'aten::div.Scalar': div_Scalar_ops_counter,
    'aten::addmm': addmm_ops_counter,
    'aten::sum.dim_IntList': sum_dim_IntList_ops_counter,
    'aten::sigmoid': sigmoid_ops_counter,
    'aten::_softmax': _soft_max_ops_counter,
    'aten::mm': mm_ops_counter,
    'aten::remainder.Scalar': remainder_Scalar_ops_counter,
    'aten::bmm': bmm_ops_counter,
    'aten::add.Tensor': add_Tensor_ops_counter,
    'aten::native_layer_norm': native_layer_norm_ops_conuter,
    'aten::mul.Tensor': mul_ops_counter, 
    'aten::mean.dim': mean_dim_ops_counter,
    'aten::gelu': gelu_ops_counter, 
    'aten::_native_batch_norm_legit_functional': _native_batch_norm_legit_functional_ops_counter,
    'aten::remainder.Tensor': remainder_Tensor_ops_counter,
    'aten::floor': floor_ops_counter,
    'aten::floor_divide': floor_divide_ops_counter,
    'aten::remainder': None,
    'aten::scatter_add': scatter_add_ops_counter,
    'aten::gelu_backward': gelu_backward_ops_counter,
    'aten::convolution_backward': convolution_backward_ops_counter,
    'aten::native_layer_norm_backward': native_layer_norm_backward_ops_counter,
    'aten::native_batch_norm_backward': native_batch_norm_backward_ops_counter,
    'aten::_softmax_backward_data': _softmax_backward_data_ops_counter,
    'aten::sigmoid_backward': sigmoid_backward_ops_counter,
}
