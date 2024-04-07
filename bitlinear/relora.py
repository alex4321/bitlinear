# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_relora.ipynb.

# %% auto 0
__all__ = ['ReLoRAOptimizer', 'is_pickleable', 'ReLoRASchedulerLambda']

# %% ../nbs/02_relora.ipynb 4
from typing import Type, Any, Dict, Iterable, Callable, Union, List
import torch
from torch.utils.data import TensorDataset, DataLoader
from .bitlinear import BitLinear
from .adapters import LoRAAdapter, MergeableLayer
from torch.optim import Adam, Optimizer
from torch.optim.lr_scheduler import LambdaLR
import gc
import pickle

# %% ../nbs/02_relora.ipynb 7
class ReLoRAOptimizer(Optimizer):
    def __init__(self,
                 params: Iterable[torch.Tensor] | Iterable[Dict[str, Any]],
                 mergeable_layers: Iterable[MergeableLayer],
                 optimizer_cls: Type[Optimizer],
                 optimizer_params: Dict[str, Any],
                 reset_n_steps: int,
                 lr: float = 1e-3,) -> None:
        params_list = list(params)
        self.inner_params = params_list
        self.optimizer_cls = optimizer_cls
        self.optimizer_params = optimizer_params
        self.lr = lr
        
        # Some trickery around param_groups require me to re-initialize stuff
        self.optimizer = self._initialize_optimizer()
        super(ReLoRAOptimizer, self).__init__(params_list, {})
        self.optimizer = self._initialize_optimizer()
        self._cleanup()

        self.mergeable_layers = mergeable_layers
        self.reset_n_steps = reset_n_steps
        self.made_steps = 0
    
    def _cleanup(self):
        gc.collect()
        torch.cuda.empty_cache()

    def _initialize_optimizer(self) -> Optimizer:
        params = dict(lr=self.lr, **self.optimizer_params)
        return self.optimizer_cls(self.inner_params, **params)
    
    def zero_grad(self, set_to_none: bool = True) -> None:
        return self.optimizer.zero_grad(set_to_none=set_to_none)
    
    def step(self, *args, **kwargs) -> None:
        self.optimizer.step(*args, **kwargs)
        if self.made_steps > 0 and self.made_steps % self.reset_n_steps == 0:
            for layer in self.mergeable_layers:
                layer.merge_adapter()
            self.optimizer = None
            self._cleanup()
            self.optimizer = self._initialize_optimizer()
        self.made_steps += 1

    @property
    def param_groups(self):
        groups = []
        for group in self.optimizer.param_groups:
            if 'lr' not in group:
                group['lr'] = self.lr
            groups.append(group)
        return groups
    
    @param_groups.setter
    def param_groups(self, groups):
        self.optimizer.param_groups = groups

    def state_dict(self) -> Dict[str, Any]:
        return self.optimizer.state_dict()
    
    def load_state_dict(self, state_dict: Dict[str, Any]) -> None:
        return self.optimizer.load_state_dict(state_dict)

# %% ../nbs/02_relora.ipynb 9
def is_pickleable(obj: Any) -> bool:
    try:
        pickle.dumps(obj)
        return True
    except:
        return False

# %% ../nbs/02_relora.ipynb 10
class ReLoRASchedulerLambda:
    def __init__(self, lr_lambda: callable, reset_n_steps: int, warmup_n_steps: int):
        assert is_pickleable(lr_lambda), "lr_lambda should be a pickleable object to use in the training process. " + \
            "Otherwise many popular trainer loop implementations will fail"
        self.func = self._wrap_lr_lambda(lr_lambda)
        self.reset_n_steps = reset_n_steps
        self.warmup_n_steps = warmup_n_steps
    
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.func(*args, **kwargs)
    
    def _wrap_lr_lambda(self, func):
        def _func(step):
            if step % self.reset_n_steps < self.warmup_n_steps:
                k = (step % self.reset_n_steps) / self.warmup_n_steps
            else:
                k = 1
            value = func(step) * k
            return value
        
        return _func
