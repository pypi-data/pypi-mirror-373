# Copyright © Nexa AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

import mlx.core as mx
import mlx.nn as nn

import os
import sys

curr_dir = os.path.dirname(os.path.abspath(__file__))
llm_common_dir = os.path.join(curr_dir, "..", "..")
sys.path.append(llm_common_dir)

from mlx_lm.models.base import (
    BaseModelArgs,
    scaled_dot_product_attention,
)
from tokenizers import Tokenizer

@dataclass
class ModelArgs(BaseModelArgs):
    model_type: str = "bert"
    vocab_size: int = 61056  # Updated from config
    hidden_size: int = 768
    num_hidden_layers: int = 12
    num_attention_heads: int = 12
    intermediate_size: int = 3072
    hidden_act: str = "gelu"
    hidden_dropout_prob: float = 0.1
    attention_probs_dropout_prob: float = 0.1
    max_position_embeddings: int = 8192  # Updated from config
    type_vocab_size: int = 2
    initializer_range: float = 0.02
    layer_norm_eps: float = 1e-12
    pad_token_id: int = 0
    position_embedding_type: str = "alibi"  # Updated from config
    use_cache: bool = True
    classifier_dropout: Optional[float] = None
    feed_forward_type: str = "geglu"  # Updated from config
    emb_pooler: str = "mean"  # Updated from config
    attn_implementation: str = "torch"


class JinaBertEmbeddings(nn.Module):
    def __init__(self, config: ModelArgs):
        super().__init__()
        self.word_embeddings = nn.Embedding(config.vocab_size, config.hidden_size)
        self.token_type_embeddings = nn.Embedding(config.type_vocab_size, config.hidden_size)
        # Use PyTorch-style naming for weight loading compatibility
        self.LayerNorm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.position_embedding_type = getattr(config, "position_embedding_type", "absolute")

    def __call__(
        self,
        input_ids: Optional[mx.array] = None,
        token_type_ids: Optional[mx.array] = None,
    ) -> mx.array:
        if token_type_ids is None:
            input_shape = input_ids.shape
            token_type_ids = mx.zeros(input_shape, dtype=mx.int64)

        inputs_embeds = self.word_embeddings(input_ids)
        token_type_embeddings = self.token_type_embeddings(token_type_ids)

        embeddings = inputs_embeds + token_type_embeddings
        embeddings = self.LayerNorm(embeddings)
        return embeddings


class JinaBertSelfAttention(nn.Module):
    def __init__(self, config: ModelArgs, position_embedding_type=None):
        super().__init__()
        if config.hidden_size % config.num_attention_heads != 0:
            raise ValueError(
                f"The hidden size ({config.hidden_size}) is not a multiple of the number of attention "
                f"heads ({config.num_attention_heads})"
            )

        self.attn_implementation = config.attn_implementation
        self.num_attention_heads = config.num_attention_heads
        self.attention_head_size = int(config.hidden_size / config.num_attention_heads)
        self.all_head_size = self.num_attention_heads * self.attention_head_size

        self.query = nn.Linear(config.hidden_size, self.all_head_size)
        self.key = nn.Linear(config.hidden_size, self.all_head_size)
        self.value = nn.Linear(config.hidden_size, self.all_head_size)

        self.position_embedding_type = position_embedding_type or getattr(
            config, "position_embedding_type", "absolute"
        )

    def transpose_for_scores(self, x: mx.array) -> mx.array:
        new_x_shape = x.shape[:-1] + (self.num_attention_heads, self.attention_head_size)
        x = x.reshape(new_x_shape)
        return x.transpose(0, 2, 1, 3)

    def __call__(
        self,
        hidden_states: mx.array,
        attention_mask: Optional[mx.array] = None,
        bias: Optional[mx.array] = None,
    ) -> mx.array:
        mixed_query_layer = self.query(hidden_states)

        key_layer = self.transpose_for_scores(self.key(hidden_states))
        value_layer = self.transpose_for_scores(self.value(hidden_states))
        query_layer = self.transpose_for_scores(mixed_query_layer)

        scale = 1.0 / math.sqrt(self.attention_head_size)

        mask = None
        if attention_mask is not None or bias is not None:
            if attention_mask is not None and bias is not None:
                mask = attention_mask + bias
            elif attention_mask is not None:
                mask = attention_mask
            else:
                mask = bias

            # Cast mask to same dtype as hidden_states
            if mask is not None:
                mask = mask.astype(hidden_states.dtype)

        context_layer = scaled_dot_product_attention(
            query_layer, key_layer, value_layer, cache=None, scale=scale, mask=mask
        )

        context_layer = context_layer.transpose(0, 2, 1, 3)
        new_context_layer_shape = context_layer.shape[:-2] + (self.all_head_size,)
        context_layer = context_layer.reshape(new_context_layer_shape)
        return context_layer


class JinaBertSelfOutput(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.dense = nn.Linear(config.hidden_size, config.hidden_size)
        # Use PyTorch-style naming for weight loading compatibility
        self.LayerNorm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)

    def __call__(self, hidden_states: mx.array, input_tensor: mx.array) -> mx.array:
        hidden_states = self.dense(hidden_states)
        hidden_states = self.LayerNorm(hidden_states + input_tensor)
        return hidden_states


class JinaBertAttention(nn.Module):
    def __init__(self, config, position_embedding_type=None):
        super().__init__()
        self.self = JinaBertSelfAttention(config, position_embedding_type=position_embedding_type)
        self.output = JinaBertSelfOutput(config)

    def __call__(
        self,
        hidden_states: mx.array,
        attention_mask: Optional[mx.array] = None,
        bias: Optional[mx.array] = None,
    ) -> mx.array:
        self_outputs = self.self(hidden_states, attention_mask, bias)
        attention_output = self.output(self_outputs, hidden_states)
        return attention_output


class JinaBertGLUMLP(nn.Module):
    def __init__(self, config: ModelArgs):
        super().__init__()
        self.config = config
        self.gated_layers = nn.Linear(config.hidden_size, config.intermediate_size * 2, bias=False)
        self.wo = nn.Linear(config.intermediate_size, config.hidden_size)
        # Use PyTorch-style naming for weight loading compatibility
        self.layernorm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)

    def __call__(self, hidden_states: mx.array) -> mx.array:
        residual_connection = hidden_states
        hidden_states = self.gated_layers(hidden_states)

        if self.config.feed_forward_type == "geglu":
            gated = hidden_states[..., : self.config.intermediate_size]
            non_gated = hidden_states[..., self.config.intermediate_size :]
            hidden_states = nn.gelu(gated) * non_gated
        else:
            # Original GLU
            gated = hidden_states[..., : self.config.intermediate_size]
            non_gated = hidden_states[..., self.config.intermediate_size :]
            hidden_states = nn.gelu(gated) * non_gated

        hidden_states = self.wo(hidden_states)
        hidden_states = self.layernorm(hidden_states + residual_connection)
        return hidden_states


class JinaBertLayer(nn.Module):
    def __init__(self, config: ModelArgs):
        super().__init__()
        self.attention = JinaBertAttention(config)
        self.feed_forward_type = config.feed_forward_type
        self.mlp = JinaBertGLUMLP(config)

    def __call__(
        self,
        hidden_states: mx.array,
        attention_mask: Optional[mx.array] = None,
        bias: Optional[mx.array] = None,
    ) -> mx.array:
        attention_output = self.attention(hidden_states, attention_mask, bias=bias)
        layer_output = self.mlp(attention_output)
        return layer_output


class JinaBertEncoder(nn.Module):
    def __init__(self, config: ModelArgs):
        super().__init__()
        self.config = config
        # Use list instead of ModuleList for PyTorch compatibility
        self.layer = [JinaBertLayer(config) for _ in range(config.num_hidden_layers)]
        self.gradient_checkpointing = False
        self.num_attention_heads = config.num_attention_heads
        self._current_alibi_size = config.max_position_embeddings

        # Build ALiBi tensor
        # self.alibi = self.rebuild_alibi_tensor(size=config.max_position_embeddings)

    def rebuild_alibi_tensor(self, size: int) -> mx.array:
        """Build ALiBi bias tensor"""
        n_heads = self.num_attention_heads

        def _get_alibi_head_slopes(n_heads: int) -> List[float]:
            def get_slopes_power_of_2(n):
                start = 2 ** (-(2 ** -(math.log2(n) - 3)))
                ratio = start
                return [start * ratio**i for i in range(n)]

            if math.log2(n_heads).is_integer():
                return get_slopes_power_of_2(n_heads)
            else:
                closest_power_of_2 = 2 ** math.floor(math.log2(n_heads))
                return (
                    get_slopes_power_of_2(closest_power_of_2)
                    + _get_alibi_head_slopes(2 * closest_power_of_2)[0::2][
                        : n_heads - closest_power_of_2
                    ]
                )

        context_position = mx.arange(size)[:, None]
        memory_position = mx.arange(size)[None, :]
        relative_position = mx.abs(memory_position - context_position)
        relative_position = mx.expand_dims(relative_position, axis=0)
        relative_position = mx.repeat(relative_position, n_heads, axis=0)

        slopes = mx.array(_get_alibi_head_slopes(n_heads)) * -1
        slopes = mx.expand_dims(mx.expand_dims(slopes, axis=1), axis=2)
        alibi = slopes * relative_position
        alibi = mx.expand_dims(alibi, axis=0)

        self._current_alibi_size = size
        return alibi

    def __call__(
        self,
        hidden_states: mx.array,
        attention_mask: Optional[mx.array] = None,
    ) -> mx.array:
        _, seqlen, _ = hidden_states.shape
        alibi_bias = self.rebuild_alibi_tensor(seqlen)

        for i, layer_module in enumerate(self.layer):
            layer_outputs = layer_module(hidden_states, attention_mask, alibi_bias)
            hidden_states = layer_outputs

        return hidden_states


class JinaBertPooler(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.dense = nn.Linear(config.hidden_size, config.hidden_size)
        self.activation = nn.tanh

    def __call__(self, hidden_states: mx.array) -> mx.array:
        # We "pool" the model by simply taking the hidden state corresponding
        # to the first token.
        first_token_tensor = hidden_states[:, 0]
        pooled_output = self.dense(first_token_tensor)
        pooled_output = self.activation(pooled_output)
        return pooled_output


class JinaBertModel(nn.Module):
    def __init__(self, config: ModelArgs):
        super().__init__()
        self.config = config
        self.embeddings = JinaBertEmbeddings(config)
        self.encoder = JinaBertEncoder(config)
        # Add pooler layer for weight compatibility
        self.pooler = JinaBertPooler(config)

    def get_extended_attention_mask(self, attention_mask: mx.array, input_shape: tuple) -> mx.array:
        """Convert attention mask to extended format"""
        if attention_mask.ndim == 3:
            extended_attention_mask = attention_mask[:, None, :, :]
        elif attention_mask.ndim == 2:
            extended_attention_mask = attention_mask[:, None, None, :]
        else:
            raise ValueError(f"Wrong shape for attention_mask (shape {attention_mask.shape})")

        extended_attention_mask = (1.0 - extended_attention_mask) * -10000.0
        return extended_attention_mask

    def mean_pooling(self, token_embeddings: mx.array, attention_mask: mx.array) -> mx.array:
        input_mask_expanded = mx.expand_dims(attention_mask, axis=-1) * mx.ones_like(
            token_embeddings
        )
        return mx.sum(token_embeddings * input_mask_expanded, axis=1) / mx.clip(
            mx.sum(input_mask_expanded, axis=1), 1e-9, None
        )

    def __call__(
        self,
        input_ids: Optional[mx.array] = None,
        attention_mask: Optional[mx.array] = None,
        token_type_ids: Optional[mx.array] = None,
    ) -> mx.array:
        input_shape = input_ids.shape

        if attention_mask is not None:
            extended_attention_mask = self.get_extended_attention_mask(attention_mask, input_shape)
        else:
            extended_attention_mask = None

        embedding_output = self.embeddings(input_ids=input_ids, token_type_ids=token_type_ids)
        encoder_outputs = self.encoder(embedding_output, attention_mask=extended_attention_mask)

        return encoder_outputs

    def encode(
        self,
        input_ids: mx.array,
        attention_mask: mx.array,
        token_type_ids: Optional[mx.array] = None,
    ) -> mx.array:
        """Encode inputs and return mean-pooled embeddings"""
        token_embs = self(
            input_ids=input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids
        )
        embeddings = self.mean_pooling(token_embs, attention_mask)
        return embeddings


class Model(nn.Module):
    def __init__(self, args: ModelArgs):
        super().__init__()
        self.args = args
        self.model_type = args.model_type
        self.model = JinaBertModel(args)

    def __call__(
        self,
        input_ids: mx.array,
        attention_mask: Optional[mx.array] = None,
        token_type_ids: Optional[mx.array] = None,
    ) -> mx.array:
        return self.model(
            input_ids=input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids
        )

    def encode(
        self,
        input_ids: mx.array,
        attention_mask: mx.array,
        token_type_ids: Optional[mx.array] = None,
    ) -> mx.array:
        """Encode inputs and return mean-pooled embeddings"""
        return self.model.encode(
            input_ids=input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids
        )

    def sanitize(self, weights):
        """Remove parameters that don't exist in our model"""
        # No longer need to remove pooler weights since we now have them
        return weights

    @property
    def layers(self):
        return self.model.encoder.layer