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

import sys
import os
import json
import mlx.core as mx
import numpy as np

curr_dir = os.path.dirname(os.path.abspath(__file__))
from .modeling.nexa_jina_v2 import Model, ModelArgs
from tokenizers import Tokenizer
from huggingface_hub import snapshot_download

def load_model(model_id):
    """Initialize and load the Jina V2 model with FP16 weights."""
    # Load configuration from config.json
    if not os.path.exists(f"{curr_dir}/modelfiles/config.json"):
        print(f"📥 Downloading model {model_id}...")
        
        # Ensure modelfiles directory exists
        os.makedirs(f"{curr_dir}/modelfiles", exist_ok=True)
        
        try:
            # Download model with progress indication
            snapshot_download(
                repo_id=model_id, 
                local_dir=f"{curr_dir}/modelfiles",
                resume_download=True,  # Resume partial downloads
                local_dir_use_symlinks=False  # Use actual files instead of symlinks
            )
            print("✅ Model download completed!")
        except Exception as e:
            print(f"❌ Failed to download model: {e}")
            print("💡 Try: huggingface-cli login (if authentication required)")
            raise

    with open(f"{curr_dir}/modelfiles/config.json", "r") as f:
        config_dict = json.load(f)
    
    # Create ModelArgs from loaded config
    config = ModelArgs(
        model_type=config_dict["model_type"],
        vocab_size=config_dict["vocab_size"],
        hidden_size=config_dict["hidden_size"],
        num_hidden_layers=config_dict["num_hidden_layers"],
        num_attention_heads=config_dict["num_attention_heads"],
        intermediate_size=config_dict["intermediate_size"],
        hidden_act=config_dict["hidden_act"],
        hidden_dropout_prob=config_dict["hidden_dropout_prob"],
        attention_probs_dropout_prob=config_dict["attention_probs_dropout_prob"],
        max_position_embeddings=config_dict["max_position_embeddings"],
        type_vocab_size=config_dict["type_vocab_size"],
        initializer_range=config_dict["initializer_range"],
        layer_norm_eps=config_dict["layer_norm_eps"],
        pad_token_id=config_dict["pad_token_id"],
        position_embedding_type=config_dict["position_embedding_type"],
        use_cache=config_dict["use_cache"],
        classifier_dropout=config_dict["classifier_dropout"],
        feed_forward_type=config_dict["feed_forward_type"],
        emb_pooler=config_dict["emb_pooler"],
        attn_implementation=config_dict["attn_implementation"],
    )
    
    # Initialize model
    model = Model(config)
    
    # Load FP16 weights
    model.load_weights(f"{curr_dir}/modelfiles/model.safetensors", strict=True)
    model.eval()
    
    return model

def load_tokenizer():
    """Load and configure the tokenizer."""
    tokenizer = Tokenizer.from_file(f"{curr_dir}/modelfiles/tokenizer.json")
    tokenizer.enable_padding(pad_id=0, pad_token="[PAD]")
    tokenizer.enable_truncation(max_length=512)
    return tokenizer

def encode_text(model, tokenizer, text):
    """Encode a single text and return its embedding."""
    # Tokenize the text
    encoding = tokenizer.encode(text)
    
    # Prepare inputs
    input_ids = np.array([encoding.ids], dtype=np.int32)
    attention_mask = np.array([encoding.attention_mask], dtype=np.float32)
    token_type_ids = np.array([encoding.type_ids if encoding.type_ids else [0] * len(encoding.ids)], dtype=np.int32)
    
    # Convert to MLX arrays
    input_ids = mx.array(input_ids)
    attention_mask = mx.array(attention_mask)
    token_type_ids = mx.array(token_type_ids)
    
    # Get embeddings
    embeddings = model.encode(
        input_ids=input_ids,
        attention_mask=attention_mask,
        token_type_ids=token_type_ids,
    )
    
    return embeddings

def main(model_id):
    """Main function to handle user input and generate embeddings."""
    
    # Load model and tokenizer
    model = load_model(model_id)
    tokenizer = load_tokenizer()
    user_input = "Hello, how are you?"
    embedding = encode_text(model, tokenizer, user_input)
    print(f"Embedding shape: {embedding.shape}")
    print(f"Embedding sample values: {embedding.flatten()[:5].tolist()}")
    print(f"Embedding min: {embedding.min()}, Max: {embedding.max()}, Mean: {embedding.mean()}, Std: {embedding.std()}")

if __name__ == "__main__":
    model_id = "nexaml/jina-v2-fp16-mlx"
    main(model_id)