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

import time
import mlx.core as mx
from .interface import create_reranker, RerankConfig


def test_reranking():
    """Test reranking model functionality."""
    # Create reranker instance
    model_path = "nexaml/jina-v2-rerank-mlx"
    reranker = create_reranker(model_path=model_path)
    
    # Load the model
    print("Loading reranking model...")
    success = reranker.load_model(model_path, extra_data="nexaml/jina-v2-rerank-mlx")
    
    if not success:
        print("Failed to load model!")
        return
    
    print("✅ Model loaded successfully!")
    
    # Test query and documents (same as generate.py)
    query = "What are the health benefits of green tea?"
    documents = [
        "Green tea is rich in antioxidants and may improve brain function.",
        "Coffee contains caffeine and can boost energy levels.",
        "Das Trinken von grünem Tee kann das Risiko für Herzkrankheiten senken.",
        "Black tea is another popular beverage with its own health benefits.",
    ]
    
    # Configure reranking with no normalization to get raw scores
    config = RerankConfig(
        batch_size=len(documents),
        normalize=False,
        normalize_method="none"
    )
    
    # Generate reranking scores
    start_time = time.time()
    scores = reranker.rerank(query, documents, config)
    end_time = time.time()
    
    # Calculate sigmoid probabilities manually  
    scores_sigmoid = mx.sigmoid(scores).tolist()
    
    inference_time = (end_time - start_time) * 1000  # Convert to ms
    
    print("=" * 70)
    print("Reranking Results:")
    print("=" * 70)
    print(f"Query: {query}")
    print()
    
    for i, (doc, score, prob) in enumerate(zip(documents, scores.tolist(), scores_sigmoid)):
        print(f"Document {i+1}:")
        print(f"  Text: {doc}")
        print(f"  Score: {score:.4f}")
        print(f"  Probability: {prob:.4f}")
        print()
    
    print(f"Inference time: {inference_time:.1f}ms")
    print(f"Throughput: {len(documents)/inference_time*1000:.1f} docs/s")
    
    # Cleanup
    reranker.close()


def main(model_id):
    """Main function to handle reranking demonstration - aligned with embedding generate.py format."""
    # Create reranker instance
    reranker = create_reranker(model_path=model_id)
    
    # Load the model
    success = reranker.load_model(model_id, extra_data=model_id)
    
    if not success:
        print("Failed to load model!")
        return
    
    # Simple test like embedding generate.py
    query = "What are the health benefits of green tea?"
    documents = [
        "Green tea is rich in antioxidants and may improve brain function.",
        "Coffee contains caffeine and can boost energy levels.",
    ]
    
    # Get raw scores
    config = RerankConfig(normalize=False)
    scores = reranker.rerank(query, documents, config)
    
    # Calculate statistics on raw MLX array
    scores_sigmoid = mx.sigmoid(scores)
    
    print(f"Scores shape: {scores.shape}")
    print(f"Score sample values: {scores.tolist()}")
    print(f"Scores min: {scores.min():.4f}, Max: {scores.max():.4f}, Mean: {scores.mean():.4f}, Std: {scores.std():.4f}")
    print(f"Sigmoid probabilities: {scores_sigmoid.tolist()}")
    
    # Cleanup
    reranker.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", type=str, default="nexaml/jina-v2-rerank-mlx")
    args = parser.parse_args()
    
    # Use test_reranking for comprehensive test, main for simple format like generate.py
    if hasattr(args, 'simple') and args.simple:
        main(args.model_path)
    else:
        test_reranking()
