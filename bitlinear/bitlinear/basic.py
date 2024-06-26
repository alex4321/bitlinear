# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/bitlinear/01_basic.ipynb.

# %% auto 0
__all__ = ['STORAGE_BIT_COUNT', 'STORAGE_DTYPE', 'STORAGE_NP_DTYPE', 'STORAGE_VALUES_PER_ITEM', 'MAPPING_UINT8_TO_5_PARAMS',
           'dequantize_weights', 'quantize_weights', 'BitLinearBasic', 'DequantizeApply', 'BitLinearDequantizing']

# %% ../../nbs/bitlinear/01_basic.ipynb 4
from typing import List, Union, Tuple, Iterable
import torch
import numpy as np
from ..adapters import LinearAdapter, LoRAAdapter, MergeableLayer
import math

# %% ../../nbs/bitlinear/01_basic.ipynb 8
STORAGE_BIT_COUNT = 8
STORAGE_DTYPE = torch.ByteTensor
STORAGE_NP_DTYPE = np.uint8

# %% ../../nbs/bitlinear/01_basic.ipynb 9
def _get_parameter_count_per_n_bits(n: int) -> int:
    i = 0
    while True:
        j = i + 1
        if 3 ** j > 2 ** n:
            break
        i += 1
    return i


STORAGE_VALUES_PER_ITEM = _get_parameter_count_per_n_bits(STORAGE_BIT_COUNT)
STORAGE_VALUES_PER_ITEM

# %% ../../nbs/bitlinear/01_basic.ipynb 12
def _generate_parameter_mappings(parameter_count: int, pad_to_size: int) -> List[List[int]]:
    def _iter(rest_count):
        if rest_count == 0:
            return [[]]
        else:
            result = []
            for p in [-1, 0, 1]:
                for rest in _iter(rest_count-1):
                    result.append([p] + rest)
            return result
    
    response = _iter(parameter_count)
    assert len(response) < pad_to_size
    response += [ [1] * parameter_count ] * (pad_to_size - len(response))
    return response


def _generate_parameter_mappings_tensor(parameter_count: int, pad_to_size: int) -> torch.Tensor:
    return torch.FloatTensor(_generate_parameter_mappings(parameter_count, pad_to_size))

# %% ../../nbs/bitlinear/01_basic.ipynb 13
MAPPING_UINT8_TO_5_PARAMS = _generate_parameter_mappings_tensor(
    STORAGE_VALUES_PER_ITEM,
    2 ** STORAGE_BIT_COUNT
)
assert MAPPING_UINT8_TO_5_PARAMS.shape == (256, 5)

# %% ../../nbs/bitlinear/01_basic.ipynb 17
@torch.no_grad
def dequantize_weights(weight_mapping: torch.Tensor, packed_weights: torch.Tensor, scale: Union[torch.Tensor, float]) \
    -> torch.Tensor:
    weights_per_item = weight_mapping.shape[-1]
    weights_packed_shape = list(packed_weights.shape[:-1]) + \
        [weights_per_item * packed_weights.shape[-1]]
    dequantized_weights_k = (scale * weight_mapping)[packed_weights.long(), :].view(weights_packed_shape)
    return dequantized_weights_k

# %% ../../nbs/bitlinear/01_basic.ipynb 19
@torch.no_grad
def quantize_weights(weights: torch.FloatTensor, mean: Union[torch.Tensor, float]) \
    -> torch.Tensor:
    weights_centered = weights - mean
    weights_sign = weights_centered.sign() + 1
    weights_sign_reshaped = weights_sign.reshape(list(weights_sign.shape)[:-1] + [-1, 5])
    weights_sign_reshaped *= torch.FloatTensor([
        3 ** 4,
        3 ** 3,
        3 ** 2,
        3 ** 1,
        3 ** 0
    ], device=weights_sign_reshaped.device).reshape([1] * (len(weights_sign_reshaped.shape) - 1) + [5])
    return weights_sign_reshaped.sum(dim=-1).to(torch.uint8)

# %% ../../nbs/bitlinear/01_basic.ipynb 24
class BitLinearBasic(MergeableLayer):
    def __init__(self,
                 in_features: int,
                 out_features: int,
                 bias: bool = True,
                 device=None,
                 dtype=None,
                 original_weights_filename: Union[str, None] = None,
                 adapter: Union[None, LinearAdapter]=None,
                 initial_linear: Union[None, torch.nn.Linear] = None):
        super(BitLinearBasic, self).__init__(adapter=adapter)

        self.in_features = in_features
        self.out_features = out_features

        if device:
            mapping = MAPPING_UINT8_TO_5_PARAMS.to(device=device)
        else:
            mapping = MAPPING_UINT8_TO_5_PARAMS * 1
        self.mapping, = self._wrap_parameters([mapping])

        self.original_weights_filename = original_weights_filename
        
        weights_linear = torch.nn.Linear(self.padded_in_features, self.padded_out_features, bias=bias, device="cpu", dtype=dtype)
        if initial_linear is not None:
            with torch.no_grad():
                weights_linear.weight.data[:initial_linear.weight.shape[0],\
                                           :initial_linear.weight.shape[1]] = initial_linear.weight.data.detach().cpu()
                if initial_linear.bias is not None:
                    weights_linear.bias.data[:] = initial_linear.bias.data
        self.mean, self.scale, self.quant_weight = self._wrap_parameters(
            self._process_params(
                *self._quantize_weight(
                    weights_linear.weight,
                    device=device
                )
            )
        )
        
        if bias:
            bias_tensor = weights_linear.bias.data
            if device is not None:
                bias_tensor = bias_tensor.to(device)
            self.bias = torch.nn.Parameter(bias_tensor)
        else:
            self.register_parameter("bias", None)
        if original_weights_filename:
            torch.save(
                weights_linear.weight,
                self.original_weights_filename,
            )        
        
        self.adapter = adapter

    @property
    def padded_in_features(self) -> int:
        return int(math.ceil(self.in_features / 5) * 5)
    
    @property
    def padded_out_features(self) -> int:
        return self.out_features
    
    def _wrap_parameters(self, tensors: Iterable[torch.Tensor]) -> List[torch.Tensor]:
        return [
            torch.nn.Parameter(tensor, requires_grad=False)
            for tensor in tensors
        ]
    
    def get_dequantized_weights(self) -> torch.Tensor:
        return dequantize_weights(self.mapping, self.quant_weight, self.scale)
    
    def get_stored_weights(self) -> torch.Tensor:
        assert self.original_weights_filename is not None
        weight = torch.load(
            self.original_weights_filename,
            map_location="cpu"
        )
        return weight

    @torch.no_grad
    def _quantize_weight(self, weight: torch.Tensor, device: str) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        weight = weight.cpu()
        mean = weight.mean().cpu()
        scale = weight.abs().mean().cpu()
        qweight = quantize_weights(weight, mean).to(device)
        return mean.to(device), scale.to(device), qweight.to(device)
    
    def pad_input(self, input: torch.Tensor) -> torch.Tensor:
        if self.padded_in_features != self.in_features:
            padding_shape = list(input.shape)[:-1] + [self.padded_in_features - self.in_features]
            padding = torch.zeros(
                padding_shape,
                dtype=input.dtype,
                device=input.device,
                requires_grad=False
            )
            padded_input = torch.cat([input, padding], dim=-1)
            return padded_input
        return input

    def forward(self, input: torch.Tensor) -> torch.Tensor:
        padded_input = self.pad_input(input)
        return self._process(padded_input)
    
    def _update_parameter(self, parameters: Iterable[torch.nn.Parameter], tensors: Iterable[torch.Tensor]) -> None:
        for parameter, tensor in zip(parameters, tensors):
            parameter.data = tensor
    
    def update_weights(self, weight: torch.Tensor) -> None:
        self._update_parameter(
            [self.mean, self.scale, self.quant_weight],
            self._process_params(
                *self._quantize_weight(weight, self.quant_weight.device)
            )
        )
        torch.save(
            weight,
            self.original_weights_filename,
        )
    
    @torch.no_grad
    def merge_adapter(self) -> None:
        assert self.adapter is not None
        self.update_weights(
            self.get_stored_weights() + self.adapter.calculate_weight_update().to("cpu")
        )
        self.adapter.reset()

    @torch.no_grad
    def _process_params(self, mean: torch.Tensor, scale: torch.Tensor, quant_weight: torch.Tensor) -> \
        Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        raise NotImplementedError("Subclass should define _process_params")

    def _process(self, padded_input: torch.Tensor) -> torch.Tensor:
        raise NotImplementedError("Subclass should define _process")

# %% ../../nbs/bitlinear/01_basic.ipynb 27
class DequantizeApply(torch.autograd.Function):
    @staticmethod
    def forward(ctx, mapping, quant_weight, scale, input):
        # Compute W in the forward pass
        if mapping.dtype != input.dtype:
            mapping = mapping.type(input.dtype)
        W = dequantize_weights(mapping, quant_weight, scale)
        ctx.save_for_backward(input, mapping, quant_weight, scale)
        return torch.nn.functional.linear(input, W)

    @staticmethod
    def backward(ctx, grad_output):
        _, mapping, quant_weight, scale = ctx.saved_tensors
        # Recompute W during the backward pass
        if mapping.dtype != grad_output.dtype:
            mapping = mapping.type(grad_output.dtype)
        W = dequantize_weights(mapping, quant_weight, scale)
        grad_input = grad_output.view([-1, grad_output.shape[-1]]).mm(W).view(list(grad_output.shape)[:-1] + [-1])
        #grad_input = grad_output.mm(W)
        # Compute other necessary gradients if needed
        # Example: grad_mapping, grad_quant_weight, grad_scale, etc.
        # These would typically be None if these tensors do not require gradients
        return None, None, None, grad_input

# %% ../../nbs/bitlinear/01_basic.ipynb 28
class BitLinearDequantizing(BitLinearBasic):
    def _process(self, padded_input: torch.Tensor) -> torch.Tensor:
        response = DequantizeApply.apply(self.mapping, self.quant_weight, self.scale, padded_input)
        if self.bias is not None:
            response += self.bias.view([1] * (len(response.shape) - 1) + [-1])
        if self.adapter:
            adapter = self.adapter(padded_input)
            response = response + adapter
        return response
    
    @torch.no_grad
    def _process_params(self, mean: torch.Tensor, scale: torch.Tensor, quant_weight: torch.Tensor) -> \
        Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        return mean, scale, quant_weight
