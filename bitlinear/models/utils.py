# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/models/02_utils.ipynb.

# %% auto 0
__all__ = ['get_submodule', 'initialize_state']

# %% ../../nbs/models/02_utils.ipynb 1
from typing import Union
import torch

# %% ../../nbs/models/02_utils.ipynb 2
def get_submodule(base: Union[None, torch.nn.Module], name: str) -> Union[None, torch.nn.Module]:
    if base is None:
        return None
    return getattr(base, name)

# %% ../../nbs/models/02_utils.ipynb 3
def initialize_state(layer: torch.nn.Module, base: Union[None, torch.nn.Module]) -> torch.nn.Module:
    if base is not None:
        assert isinstance(layer, type(base)), "layer should have the same type as base layer"
        layer.load_state_dict(base.state_dict())
    return layer
