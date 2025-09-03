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

import os

from .interface import create_cv_model, CVModelConfig


def test_cv_model(model_path, test_image_path):
    """Test CV model functionality."""
    
    # Create CVModelConfig
    config = CVModelConfig(
        capabilities=0,  # ML_CV_OCR
        model_path=model_path,
        system_library_path=None,
        backend_library_path=None,
        extension_library_path=None,
        config_file_path=None,
        char_dict_path=None
    )
    
    model = create_cv_model(config)
    print("✅ Model loaded successfully!")
    
    # Test images (you can replace these with actual image paths)
    test_images = [
        "cv/modeling/input/20250406-170821.jpeg",
        "cv/modeling/input/20250406-170838.jpeg",
        "cv/modeling/input/20250406-170906.jpeg",
        "cv/modeling/input/20250407-154044.jpeg",
        "cv/modeling/input/20250407-154059.jpeg"
    ] if test_image_path is None else [test_image_path]
    
    for img_path in test_images:
        if not os.path.exists(img_path):
            print(f"❌ Image file not found: {img_path}")
            continue
        
        results = model.infer(img_path)
        print(f"✅ OCR Results for {img_path}:")
        print("=" * 50)

        if results.result_count == 0:
            print("No text detected in the image.")
        else:
            print(f"Found {results.result_count} text regions:")
            
            for i, result in enumerate(results.results):
                print(f"\nRegion {i+1}:")
                print(f"  Text: '{result.text}'")
                print(f"  Confidence: {result.confidence:.3f}")
    
    print("\n✅ CV model test completed!")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Test CV processor functionality")
    parser.add_argument("--model_path", type=str, default="nexaml/paddle-ocr-mlx", 
                       help="Path to the CV model")
    parser.add_argument("--image_path", type=str, default=None,
                       help="Path to a specific image to process")
    parser.add_argument("--test_mode", action="store_true",
                       help="Run in test mode with sample images")
    
    args = parser.parse_args()
    
    test_cv_model(args.model_path, args.image_path) 
    