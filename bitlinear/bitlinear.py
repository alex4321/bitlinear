# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/01_bitlinear.ipynb.

# %% auto 0
__all__ = ['STORAGE_BIT_COUNT', 'STORAGE_DTYPE', 'STORAGE_VALUES_PER_ITEM', 'MAPPING_UINT8_TO_5_PARAMS', 'dequantize_weights',
           'quantize_weights', 'BitLinear']

# %% ../nbs/01_bitlinear.ipynb 4
from typing import List, Union, Tuple, Iterable
import torch
from .adapters import LinearAdapter, LoRAAdapter, MergeableLayer

# %% ../nbs/01_bitlinear.ipynb 7
STORAGE_BIT_COUNT = 8
STORAGE_DTYPE = torch.ByteTensor

# %% ../nbs/01_bitlinear.ipynb 8
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

# %% ../nbs/01_bitlinear.ipynb 11
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

# %% ../nbs/01_bitlinear.ipynb 12
MAPPING_UINT8_TO_5_PARAMS = _generate_parameter_mappings_tensor(
    STORAGE_VALUES_PER_ITEM,
    2 ** STORAGE_BIT_COUNT
)
assert MAPPING_UINT8_TO_5_PARAMS.shape == (256, 5)

# %% ../nbs/01_bitlinear.ipynb 15
@torch.no_grad
def dequantize_weights(weight_mapping: torch.Tensor, packed_weights: torch.Tensor, scale: Union[torch.Tensor, float]) \
    -> torch.Tensor:
    weights_per_item = weight_mapping.shape[-1]
    weights_packed_shape = list(packed_weights.shape[:-1]) + \
        [weights_per_item * packed_weights.shape[-1]]
    dequantized_weights_k = weight_mapping[packed_weights.long(), :].view(weights_packed_shape)
    return dequantized_weights_k * scale

# %% ../nbs/01_bitlinear.ipynb 17
@torch.no_grad
def quantize_weights(weight_mapping: torch.FloatTensor, weights: torch.FloatTensor, mean: Union[torch.Tensor, float]) \
    -> torch.Tensor:
    weights_centered = weights - mean
    weights_sign = weights_centered.sign()
    weights_reshaped = weights_sign.view(
        list(weights_sign.shape[:-1]) + [weights_sign.shape[-1] // STORAGE_VALUES_PER_ITEM, 1, STORAGE_VALUES_PER_ITEM]
    )
    weight_mapping_reshaped = weight_mapping.view(
        [1] * len(weights_sign.shape) + [2 ** STORAGE_BIT_COUNT, STORAGE_VALUES_PER_ITEM]
    )
    weights_mapping_diff = (weights_reshaped - weight_mapping_reshaped).abs()
    weights_group_scores = weights_mapping_diff.sum(dim=-1)
    weigths_group_chosen = weights_group_scores.argmin(dim=-1)
    weigths_group_chosen.clamp_(0, 3 ** STORAGE_VALUES_PER_ITEM - 1)
    return weigths_group_chosen.byte()

# %% ../nbs/01_bitlinear.ipynb 20
class BitLinear(MergeableLayer):
    def __init__(self,
                 in_features: int,
                 out_features: int,
                 bias: bool = True,
                 device=None,
                 dtype=None,
                 original_weights_filename: Union[str, None] = None,
                 adapter: Union[None, LinearAdapter]=None):
        super(BitLinear, self).__init__(adapter=adapter)
        assert in_features % STORAGE_VALUES_PER_ITEM == 0

        if device:
            self.mapping = MAPPING_UINT8_TO_5_PARAMS.to(device=device)
        else:
            self.mapping = MAPPING_UINT8_TO_5_PARAMS * 1
        self.mapping_cpu = MAPPING_UINT8_TO_5_PARAMS * 1
            

        self.original_weights_filename = original_weights_filename
        
        initial_linear = torch.nn.Linear(in_features, out_features, bias=bias, device="cpu", dtype=dtype)
        self.mean, self.scale, self.quant_weight = self._wrap_parameters(self._quantize_weight(
            initial_linear.weight,
            device=device
        ))
        
        if bias:
            bias_tensor = initial_linear.bias.data
            if device is not None:
                bias_tensor = bias_tensor.to(device)
            self.bias = torch.nn.Parameter(bias_tensor)
        else:
            self.register_parameter("bias", None)
        if original_weights_filename:
            torch.save(
                initial_linear.weight,
                self.original_weights_filename,
            )        
        
        self.adapter = adapter

    def _wrap_parameters(self, tensors: Iterable[torch.Tensor]) -> List[torch.Tensor]:
        return [
            torch.nn.Parameter(tensor, requires_grad=False)
            for tensor in tensors
        ]

    @torch.no_grad
    def _quantize_weight(self, weight: torch.Tensor, device: str) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        weight = weight.cpu()
        mean = weight.mean().cpu()
        scale = weight.abs().mean().cpu()
        qweight = quantize_weights(self.mapping_cpu, weight, mean).to(device)
        return mean.to(device), scale.to(device), qweight.to(device)

    def forward(self, input: torch.Tensor) -> torch.Tensor:
        W = dequantize_weights(self.mapping, self.quant_weight, self.scale)
        response = torch.nn.functional.linear(input, W, self.bias)
        if self.adapter:
            adapter = self.adapter(input)
            response = response + adapter
        return response
    
    def _update_parameter(self, parameters: Iterable[torch.nn.Parameter], tensors: Iterable[torch.Tensor]) -> None:
        for parameter, tensor in zip(parameters, tensors):
            parameter.data = tensor
    
    @torch.no_grad
    def _update_weight(self, update: torch.Tensor) -> None:
        assert self.original_weights_filename is not None
        weight = torch.load(
            self.original_weights_filename,
            map_location="cpu"
        )
        weight_updated = weight + update.to("cpu")
        self._update_parameter(
            [self.mean, self.scale, self.quant_weight],
            self._quantize_weight(weight_updated, self.quant_weight.device)
        )
        torch.save(
            weight_updated,
            self.original_weights_filename,
        )

    def merge_adapter(self) -> None:
        assert self.adapter is not None
        self._update_weight(
            self.adapter.calculate_weight_update()
        )
        self.adapter.reset()
