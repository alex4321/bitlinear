# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/models/03_mistral.ipynb.

# %% auto 0
__all__ = ['BITMISTRAL_ATTENTION_CLASSES', 'BitMistralMLP', 'BitMistralAttentionBase', 'BitMistralAttention',
           'BitMistralFlashAttention2', 'BitMistralSdpaAttention', 'BitMistralDecoderLayer',
           'BitMistralPreTrainedModel', 'BitMistralAdaptersMixin', 'BitMistralModel', 'BitMistralForCausalLM',
           'BitMistralForSequenceClassification']

# %% ../../nbs/models/03_mistral.ipynb 1
"""
Modified code for Mistral model
"""
from typing import List, Optional, Type, Any, Dict, Union

import torch
import torch.nn.functional as F
import torch.utils.checkpoint
from torch import nn

from transformers.activations import ACT2FN
from transformers.models.mistral.configuration_mistral import MistralConfig

from transformers.models.mistral.modeling_mistral import \
    is_flash_attn_2_available, is_flash_attn_greater_or_equal_2_10, \
    MistralRMSNorm, \
    MistralRotaryEmbedding, \
    MistralMLP, MistralAttention, \
    MistralFlashAttention2, \
    MistralSdpaAttention, \
    MistralDecoderLayer, \
    MistralPreTrainedModel, \
    MistralModel, \
    MistralForCausalLM, \
    MistralForSequenceClassification

from ..bitlinear import BitLinear
from ..adapters import LinearAdapter, LoRAAdapter, MergeableLayer
from .utils import initialize_state, get_submodule

# %% ../../nbs/models/03_mistral.ipynb 2
class BitMistralMLP(MistralMLP):
    def __init__(self, config: MistralConfig, fname_prefix: str, base: Union[None, MistralMLP] = None):
        nn.Module.__init__(self)
        self.config = config
        self.hidden_size = config.hidden_size
        self.intermediate_size = config.intermediate_size
        self.gate_proj = BitLinear(
            in_features=self.hidden_size,
            out_features=self.intermediate_size,
            bias=False,
            original_weights_filename=f"{fname_prefix}-gate-proj.bin",
            initial_linear=None if base is None else base.gate_proj
        )
        self.up_proj = BitLinear(
            in_features=self.hidden_size,
            out_features=self.intermediate_size,
            bias=False,
            original_weights_filename=f"{fname_prefix}-up-proj.bin",
            initial_linear=None if base is None else base.up_proj
        )
        self.down_proj = BitLinear(
            in_features=self.intermediate_size,
            out_features=self.hidden_size,
            bias=False,
            original_weights_filename=f"{fname_prefix}-down-proj.bin",
            initial_linear=None if base is None else base.down_proj
        )
        self.act_fn = initialize_state(
            ACT2FN[config.hidden_act],
            get_submodule(base, 'act_fn')
        )

# %% ../../nbs/models/03_mistral.ipynb 3
class BitMistralAttentionBase:
    def __init__(self, config: MistralConfig, fname_prefix: str, layer_idx: Optional[int] = None, base: Union[None, MistralAttention] = None):
        nn.Module.__init__(self)
        self.config = config
        self.layer_idx = layer_idx
        assert layer_idx is not None

        self.hidden_size = config.hidden_size
        self.num_heads = config.num_attention_heads
        self.head_dim = self.hidden_size // self.num_heads
        self.num_key_value_heads = config.num_key_value_heads
        self.num_key_value_groups = self.num_heads // self.num_key_value_heads
        self.max_position_embeddings = config.max_position_embeddings
        self.rope_theta = config.rope_theta
        self.is_causal = True
        self.attention_dropout = config.attention_dropout

        if (self.head_dim * self.num_heads) != self.hidden_size:
            raise ValueError(
                f"hidden_size must be divisible by num_heads (got `hidden_size`: {self.hidden_size}"
                f" and `num_heads`: {self.num_heads})."
            )
        self.q_proj = BitLinear(
            self.hidden_size,
            self.num_heads * self.head_dim,
            bias=False,
            original_weights_filename=f"{fname_prefix}-q-proj.bin",
            initial_linear=None if base is None else base.q_proj
        )
        self.k_proj = BitLinear(
            self.hidden_size,
            self.num_key_value_heads * self.head_dim,
            bias=False,
            original_weights_filename=f"{fname_prefix}-k-proj.bin",
            initial_linear=None if base is None else base.k_proj
        )
        self.v_proj = BitLinear(
            self.hidden_size,
            self.num_key_value_heads * self.head_dim,
            bias=False,
            original_weights_filename=f"{fname_prefix}-v-proj.bin",
            initial_linear=None if base is None else base.v_proj
        )
        self.o_proj = BitLinear(
            self.num_heads * self.head_dim,
            self.hidden_size,
            bias=False,
            original_weights_filename=f"{fname_prefix}-o-proj.bin",
            initial_linear=None if base is None else base.o_proj
        )

        self.rotary_emb = initialize_state(
            MistralRotaryEmbedding(
                self.head_dim,
                max_position_embeddings=self.max_position_embeddings,
                base=self.rope_theta,
            ),
            get_submodule(base, 'rotary_emb')
        )


class BitMistralAttention(MistralAttention, BitMistralAttentionBase):
    def __init__(self, config: MistralConfig, fname_prefix: str, layer_idx: Optional[int] = None, base: Union[None, MistralAttention] = None):
        BitMistralAttentionBase.__init__(self, config, fname_prefix, layer_idx, base)


class BitMistralFlashAttention2(MistralFlashAttention2, BitMistralAttentionBase):
    def __init__(self, config: MistralConfig, fname_prefix: str, layer_idx: Optional[int] = None, base: Union[None, MistralFlashAttention2] = None):
        BitMistralAttentionBase.__init__(self, config, fname_prefix, layer_idx, base)
        self._flash_attn_uses_top_left_mask = not is_flash_attn_greater_or_equal_2_10()


class BitMistralSdpaAttention(MistralSdpaAttention, BitMistralAttentionBase):
    def __init__(self, config: MistralConfig, fname_prefix: str, layer_idx: Optional[int] = None, base: Union[None, MistralSdpaAttention] = None):
        BitMistralAttentionBase.__init__(self, config, fname_prefix, layer_idx, base)

# %% ../../nbs/models/03_mistral.ipynb 4
BITMISTRAL_ATTENTION_CLASSES = {
    "eager": BitMistralAttention,
    "flash_attention_2": BitMistralFlashAttention2,
    "sdpa": BitMistralSdpaAttention,
}

# %% ../../nbs/models/03_mistral.ipynb 5
class BitMistralDecoderLayer(MistralDecoderLayer):
    def __init__(self, config: MistralConfig, layer_idx: int, fname_prefix: str, base: Union[None, MistralDecoderLayer] = None):
        nn.Module.__init__(self)
        self.hidden_size = config.hidden_size

        self.layer_idx = layer_idx
        self.self_attn = BITMISTRAL_ATTENTION_CLASSES[config._attn_implementation](
            config=config,
            fname_prefix=f"{fname_prefix}-self-attn.bin",
            layer_idx=layer_idx,
            base=None if base is None else base.self_attn
        )
        self.mlp = BitMistralMLP(
            config=config,
            fname_prefix=f"{fname_prefix}-mlp.bin",
            base=None if base is None else base.mlp
        )
        self.input_layernorm = initialize_state(
            MistralRMSNorm(config.hidden_size, eps=config.rms_norm_eps),
            get_submodule(base, 'input_layernorm')
        )
        self.post_attention_layernorm = initialize_state(
            MistralRMSNorm(config.hidden_size, eps=config.rms_norm_eps),
            get_submodule(base, 'post_attention_layernorm')
        )

# %% ../../nbs/models/03_mistral.ipynb 6
class BitMistralPreTrainedModel(MistralPreTrainedModel):
    def _init_weights(self, module):
        std = self.config.initializer_range
        if isinstance(module, nn.Linear):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.bias is not None:
                module.bias.data.zero_()
        if isinstance(module, BitLinear):
            module.update_weights(
                torch.normal(
                    mean=torch.zeros(module.out_features, module.in_features),
                    std=torch.ones(module.out_features, module.in_features) * std,
                )
            )
            if module.bias is not None:
                module.bias.zero_()
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.padding_idx is not None:
                module.weight.data[module.padding_idx].zero_()
    

class BitMistralAdaptersMixin(nn.Module):
    def _get_bitlinear_layers(self) -> List[BitLinear]:
        layers = []
        for layer in self.modules():
            if isinstance(layer, BitLinear):
                layers.append(layer)
        return layers
    
    def add_adapters(self, adapter_type: Type[LinearAdapter], params: Dict[str, Any]) -> List[LinearAdapter]:
        layers = self._get_bitlinear_layers()
        adapters = []
        for layer in layers:
            layer_params = dict(**params)
            layer_params["in_features"] = layer.padded_in_features
            layer_params["out_features"] = layer.padded_out_features
            layer_params["device"] = layer.quant_weight.device
            adapter = adapter_type(**layer_params)
            layer.adapter = adapter
            adapters.append(adapter)
        return adapters
    
    def remove_adapters(self) -> None:
        layers = self._get_bitlinear_layers()
        for layer in layers:
            if layer.adapter is not None:
                layer.adapter = None


    def mergeable_layers(self) -> List[MergeableLayer]:
        layers = []
        for layer in self.modules():
            if isinstance(layer, MergeableLayer):
                layers.append(layer)
        return layers

# %% ../../nbs/models/03_mistral.ipynb 7
class BitMistralModel(MistralModel, BitMistralAdaptersMixin):
    def __init__(self, config: MistralConfig, fname_prefix: str, base: Union[None, MistralModel] = None):
        BitMistralPreTrainedModel.__init__(self, config)
        self.padding_idx = config.pad_token_id
        self.vocab_size = config.vocab_size

        self.embed_tokens = initialize_state(
            nn.Embedding(config.vocab_size, config.hidden_size, self.padding_idx),
            get_submodule(base, 'embed_tokens')
        )
        self.layers = nn.ModuleList(
            [
                BitMistralDecoderLayer(
                    config,
                    layer_idx,
                    f"{fname_prefix}-decoder-{layer_idx}",
                    base=None if base is None else base.layers[layer_idx]
                )
                for layer_idx in range(config.num_hidden_layers)
            ]
        )
        self._attn_implementation = config._attn_implementation
        self.norm = initialize_state(
            MistralRMSNorm(config.hidden_size, eps=config.rms_norm_eps),
            get_submodule(base, 'norm')
        )

        self.gradient_checkpointing = False
        # Initialize weights and apply final processing
        self.post_init()

# %% ../../nbs/models/03_mistral.ipynb 8
class BitMistralForCausalLM(MistralForCausalLM, BitMistralAdaptersMixin):
    def __init__(self, config: MistralConfig, fname_prefix: str, base: Union[None, MistralForCausalLM] = None):
        BitMistralPreTrainedModel.__init__(self, config)
        self.model = BitMistralModel(config, fname_prefix, base=None if base is None else base.model)
        self.vocab_size = config.vocab_size
        self.lm_head = initialize_state(
            nn.Linear(config.hidden_size, config.vocab_size, bias=False),
            get_submodule(base, 'lm_head')
        )

        # Initialize weights and apply final processing
        if base is None:
            self.post_init()

# %% ../../nbs/models/03_mistral.ipynb 9
class BitMistralForSequenceClassification(MistralForSequenceClassification, BitMistralAdaptersMixin):
    def __init__(self, config: MistralConfig, fname_prefix: str, base: Union[None, MistralForSequenceClassification] = None):
        BitMistralPreTrainedModel.__init__(self, config)
        self.num_labels = config.num_labels
        self.model = MistralModel(config, fname_prefix, base=None if base is None else base.model)
        self.score = initialize_state(
            nn.Linear(config.hidden_size, self.num_labels, bias=False),
            get_submodule(base, 'score')
        )

        # Initialize weights and apply final processing
        if base is None:
            self.post_init()
