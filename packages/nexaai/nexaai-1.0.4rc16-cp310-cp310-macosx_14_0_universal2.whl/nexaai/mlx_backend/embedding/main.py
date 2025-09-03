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

from .interface import create_embedder, EmbeddingConfig


def test_embedding(model_path):
    """Test embedding model functionality."""
    embedder = create_embedder(model_path=model_path)
    
    # Load the model
    print("Loading embedding model...")
    success = embedder.load_model(model_path)
    
    if not success:
        print("Failed to load model!")
        return
    
    print("✅ Model loaded successfully!")
    print(f"Embedding dimension: {embedder.embedding_dim()}")
    
    # Test texts
    test_texts = [
        "Hello, how are you?",
        "What is machine learning?",
        "The weather is nice today.",
        "Python is a programming language."
    ]
    
    # Configure embedding
    config = EmbeddingConfig(
        batch_size=2,
        normalize=True,
        normalize_method="l2"
    )
    
    print(f"\nGenerating embeddings for {len(test_texts)} texts...")
    
    # Generate embeddings
    embeddings = embedder.embed(test_texts, config)
    
    # Display results
    print("\nEmbedding Results:")
    print("=" * 50)
    
    for i, (text, embedding) in enumerate(zip(test_texts, embeddings)):
        print(f"\nText {i+1}: '{text}'")
        print(f"Embedding shape: {len(embedding)}")
        print(f"First 5 values: {embedding[:5]}")
        
        # Calculate magnitude for normalized embeddings
        magnitude = sum(x*x for x in embedding) ** 0.5
        print(f"Magnitude: {magnitude:.6f}")
    
    # Test similarity between first two embeddings
    if len(embeddings) >= 2:
        emb1, emb2 = embeddings[0], embeddings[1]
        similarity = sum(a*b for a, b in zip(emb1, emb2))
        print(f"\nCosine similarity between text 1 and 2: {similarity:.6f}")
    
    # Cleanup
    embedder.close()
    print("\n✅ Embedding test completed!")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", type=str, default="nexaml/jina-v2-fp16-mlx")
    args = parser.parse_args()
    test_embedding(args.model_path)
