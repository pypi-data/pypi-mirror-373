# Copyright © 2023-2024 Apple Inc.

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

import mlx.core as mx
import mlx.nn as nn

from mlx_lm.models.base import (
    BaseModelArgs,
    scaled_dot_product_attention,
)


@dataclass
class ModelArgs(BaseModelArgs):
    model_type: str = "xlm_roberta"
    vocab_size: int = 250002
    hidden_size: int = 768
    num_hidden_layers: int = 12
    num_attention_heads: int = 12
    intermediate_size: int = 3072
    hidden_act: str = "gelu"
    hidden_dropout_prob: float = 0.1
    attention_probs_dropout_prob: float = 0.1
    max_position_embeddings: int = 1026
    type_vocab_size: int = 1
    initializer_range: float = 0.02
    layer_norm_eps: float = 1e-05
    pad_token_id: int = 1
    bos_token_id: int = 0
    eos_token_id: int = 2
    position_embedding_type: str = "absolute"
    use_cache: bool = True
    classifier_dropout: Optional[float] = None
    num_labels: int = 1


class XLMRobertaEmbeddings(nn.Module):
    def __init__(self, config: ModelArgs):
        super().__init__()
        self.word_embeddings = nn.Embedding(config.vocab_size, config.hidden_size)
        self.position_embeddings = nn.Embedding(config.max_position_embeddings, config.hidden_size)
        self.token_type_embeddings = nn.Embedding(config.type_vocab_size, config.hidden_size)

    def __call__(
        self,
        input_ids: Optional[mx.array] = None,
        position_ids: Optional[mx.array] = None,
        token_type_ids: Optional[mx.array] = None,
    ) -> mx.array:
        if token_type_ids is None:
            token_type_ids = mx.zeros_like(input_ids)

        inputs_embeds = self.word_embeddings(input_ids)
        position_embeddings = self.position_embeddings(position_ids)
        token_type_embeddings = self.token_type_embeddings(token_type_ids)

        embeddings = inputs_embeds + position_embeddings + token_type_embeddings
        return embeddings


class SelfAttention(nn.Module):
    def __init__(self, config: ModelArgs):
        super().__init__()
        self.num_attention_heads = config.num_attention_heads
        self.attention_head_size = int(config.hidden_size / config.num_attention_heads)
        self.all_head_size = self.num_attention_heads * self.attention_head_size

    def __call__(
        self,
        qkv: mx.array,
        key_padding_mask: Optional[mx.array] = None,
    ) -> mx.array:
        # qkv shape: [batch, seqlen, 3, num_heads, head_dim]
        batch_size, seqlen = qkv.shape[0], qkv.shape[1]
        q, k, v = mx.split(qkv, 3, axis=2)  # Each: [batch, seqlen, 1, num_heads, head_dim]
        q = mx.squeeze(q, axis=2)  # [batch, seqlen, num_heads, head_dim]
        k = mx.squeeze(k, axis=2)
        v = mx.squeeze(v, axis=2)

        # Transpose for attention computation: [batch, num_heads, seqlen, head_dim]
        q = mx.transpose(q, (0, 2, 1, 3))
        k = mx.transpose(k, (0, 2, 1, 3))
        v = mx.transpose(v, (0, 2, 1, 3))

        scale = 1.0 / math.sqrt(self.attention_head_size)

        mask = None
        if key_padding_mask is not None:
            # key_padding_mask: [batch, seqlen] where True means keep, False means mask
            # Convert to attention mask: [batch, 1, 1, seqlen]
            mask = mx.expand_dims(mx.expand_dims(key_padding_mask, axis=1), axis=1)
            # Use the same dtype as the query tensor to match model dtype
            target_dtype = q.dtype
            mask = (1.0 - mask.astype(target_dtype)) * -10000.0

        context = scaled_dot_product_attention(q, k, v, cache=None, scale=scale, mask=mask)

        # Transpose back and reshape: [batch, seqlen, hidden_size]
        context = mx.transpose(context, (0, 2, 1, 3))
        new_context_shape = context.shape[:-2] + (self.all_head_size,)
        context = mx.reshape(context, new_context_shape)
        return context


class MHA(nn.Module):
    def __init__(self, config: ModelArgs):
        super().__init__()
        self.embed_dim = config.hidden_size
        self.num_heads = config.num_attention_heads
        self.head_dim = self.embed_dim // self.num_heads

        # QKV projection
        qkv_dim = self.head_dim * (self.num_heads + 2 * self.num_heads)  # q + k + v
        self.Wqkv = nn.Linear(self.embed_dim, qkv_dim, bias=True)

        # Self attention
        self.inner_attn = SelfAttention(config)

        # Output projection
        self.out_proj = nn.Linear(self.embed_dim, self.embed_dim, bias=True)

    def __call__(
        self,
        x: mx.array,
        key_padding_mask: Optional[mx.array] = None,
    ) -> tuple:
        residual = x
        qkv = self.Wqkv(x)

        # Reshape to [batch, seqlen, 3, num_heads, head_dim]
        batch, seqlen = qkv.shape[0], qkv.shape[1]
        qkv = mx.reshape(qkv, (batch, seqlen, 3, self.num_heads, self.head_dim))

        context = self.inner_attn(qkv, key_padding_mask=key_padding_mask)
        out = self.out_proj(context)

        return out, residual


class Mlp(nn.Module):
    def __init__(self, config: ModelArgs):
        super().__init__()
        self.fc1 = nn.Linear(config.hidden_size, config.intermediate_size, bias=True)
        self.fc2 = nn.Linear(config.intermediate_size, config.hidden_size, bias=True)

    def __call__(self, x: mx.array) -> tuple:
        residual = x
        y = self.fc1(x)
        y = nn.gelu(y)
        y = self.fc2(y)
        return y, residual


class Block(nn.Module):
    def __init__(self, config: ModelArgs):
        super().__init__()
        self.mixer = MHA(config)
        self.norm1 = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.mlp = Mlp(config)
        self.norm2 = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)

    def __call__(
        self,
        hidden_states: mx.array,
        mixer_kwargs: Optional[dict] = None,
    ) -> mx.array:
        mixer_kwargs = mixer_kwargs or {}

        # Attention block
        mixer_out, residual = self.mixer(hidden_states, **mixer_kwargs)
        hidden_states = self.norm1(mixer_out + residual)

        # MLP block
        mlp_out, residual = self.mlp(hidden_states)
        hidden_states = self.norm2(mlp_out + residual)

        return hidden_states


class XLMRobertaEncoder(nn.Module):
    def __init__(self, config: ModelArgs):
        super().__init__()
        # Create layers list to match torch naming
        self.layers = [Block(config) for _ in range(config.num_hidden_layers)]

    def __call__(
        self,
        hidden_states: mx.array,
        key_padding_mask: Optional[mx.array] = None,
    ) -> mx.array:
        mixer_kwargs = None
        if key_padding_mask is not None:
            mixer_kwargs = {"key_padding_mask": key_padding_mask}

        # Access layers from the list
        for layer_module in self.layers:
            hidden_states = layer_module(hidden_states, mixer_kwargs=mixer_kwargs)

        return hidden_states


class XLMRobertaModel(nn.Module):
    def __init__(self, config: ModelArgs):
        super().__init__()
        self.config = config
        self.embeddings = XLMRobertaEmbeddings(config)
        self.emb_ln = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.encoder = XLMRobertaEncoder(config)

    def __call__(
        self,
        input_ids: mx.array,
        attention_mask: Optional[mx.array] = None,
        token_type_ids: Optional[mx.array] = None,
        position_ids: Optional[mx.array] = None,
    ) -> mx.array:
        hidden_states = self.embeddings(
            input_ids=input_ids,
            position_ids=position_ids,
            token_type_ids=token_type_ids,
        )

        hidden_states = self.emb_ln(hidden_states)

        # Convert attention_mask for padding (True=keep, False=mask)
        key_padding_mask = attention_mask

        sequence_output = self.encoder(hidden_states, key_padding_mask=key_padding_mask)

        return sequence_output


class XLMRobertaClassificationHead(nn.Module):
    def __init__(self, config: ModelArgs):
        super().__init__()
        self.dense = nn.Linear(config.hidden_size, config.hidden_size)
        self.out_proj = nn.Linear(config.hidden_size, config.num_labels)

    def __call__(self, features: mx.array) -> mx.array:
        x = features[:, 0, :]  # take first token (equivalent to [CLS])
        x = self.dense(x)
        x = mx.tanh(x)
        x = self.out_proj(x)
        return x


class XLMRobertaForSequenceClassification(nn.Module):
    def __init__(self, config: ModelArgs):
        super().__init__()
        self.num_labels = config.num_labels
        self.config = config
        self.roberta = XLMRobertaModel(config)
        self.classifier = XLMRobertaClassificationHead(config)

    def __call__(
        self,
        input_ids: mx.array,
        attention_mask: Optional[mx.array] = None,
        token_type_ids: Optional[mx.array] = None,
        position_ids: Optional[mx.array] = None,
    ) -> mx.array:
        sequence_output = self.roberta(
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
        )
        logits = self.classifier(sequence_output)
        return logits

    def nexa_forward(
        self,
        input_ids: mx.array,
        attention_mask: mx.array,
        token_type_ids: mx.array,
        position_ids: mx.array,
    ) -> mx.array:
        return self(
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
        )


class Model(nn.Module):
    def __init__(self, args: ModelArgs):
        super().__init__()
        self.args = args
        self.model_type = args.model_type
        self.model = XLMRobertaForSequenceClassification(args)

    def __call__(
        self,
        input_ids: mx.array,
        attention_mask: Optional[mx.array] = None,
        token_type_ids: Optional[mx.array] = None,
        position_ids: Optional[mx.array] = None,
    ) -> mx.array:
        return self.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
        )

    def nexa_forward(
        self,
        input_ids: mx.array,
        attention_mask: mx.array,
        token_type_ids: mx.array,
        position_ids: mx.array,
    ) -> mx.array:
        return self.model.nexa_forward(
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
        )

    def sanitize(self, weights):
        """Remove parameters that don't exist in our model"""
        return weights

    @property
    def layers(self):
        return self.model.roberta.encoder.layers