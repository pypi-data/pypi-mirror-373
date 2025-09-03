from interface import ImageGen, ImageGenerationConfig, ImageSamplerConfig, Image
import numpy as np
from PIL import Image as PILImage
import mlx.core as mx


def test_txt2image(
    prompt="A photo of an astronaut riding a horse on Mars.",
    model="sdxl",
    local_model_path="",
    n_images=1,
    steps=None,
    cfg=None,
    negative_prompt="",
    n_rows=1,
    decoding_batch_size=1,
    float16=True,
    quantize=False,
    preload_models=False,
    output="out_txt2img.png",
    seed=None,
    verbose=False,
    width=512,
    height=512,
):
    """Generate images from text prompt using high-level interface"""

    # Determine model path based on model type
    if model == "sdxl":
        model_path = local_model_path or "stabilityai/sdxl-turbo"
        default_cfg = 0.0
        default_steps = 2
    else:
        model_path = local_model_path or "stabilityai/stable-diffusion-2-1-base"
        default_cfg = 7.5
        default_steps = 50

    # Use provided values or defaults
    cfg = cfg or default_cfg
    steps = steps or default_steps

    # Create ImageGen instance with proper parameters
    image_gen = ImageGen(model_path, "", device=None, float16=float16, quantize=quantize)

    # Load the model
    if not image_gen.load_model(model_path):
        print(f"Failed to load model: {model_path}")
        return None

    # Create sampler configuration
    sampler_config = ImageSamplerConfig(
        method="ddim",
        steps=steps,
        guidance_scale=cfg,
        seed=seed if seed is not None else -1,
    )

    # Create generation configuration with all parameters
    gen_config = ImageGenerationConfig(
        prompts=prompt,
        negative_prompts=negative_prompt,
        height=height,
        width=width,
        sampler_config=sampler_config,
        n_images=n_images,
        n_rows=n_rows,
        decoding_batch_size=decoding_batch_size,
    )

    if verbose:
        print(f"Generating {n_images} image(s) with prompt: '{prompt}'")
        print(f"Model: {model_path}, Steps: {steps}, CFG: {cfg}")
        print(f"Float16: {float16}, Quantize: {quantize}")

    # Generate image using txt2img
    result_image = image_gen.txt2img(prompt, gen_config)

    # Free memory by deleting model components (following main_duplicate.py pattern)
    if image_gen.model:
        if model == "sdxl":
            if hasattr(image_gen.model, "text_encoder_1"):
                del image_gen.model.text_encoder_1
            if hasattr(image_gen.model, "text_encoder_2"):
                del image_gen.model.text_encoder_2
        else:
            if hasattr(image_gen.model, "text_encoder"):
                del image_gen.model.text_encoder

        if hasattr(image_gen.model, "unet"):
            del image_gen.model.unet
        if hasattr(image_gen.model, "sampler"):
            del image_gen.model.sampler

    # Get peak memory usage
    peak_mem_unet = mx.metal.get_peak_memory() / 1024**3

    # Convert to PIL and save
    image_np = result_image.to_numpy()
    image_pil = PILImage.fromarray((image_np * 255).astype(np.uint8))
    image_pil.save(output)

    print(f"Text-to-image output saved to: {output}")

    # Get final peak memory usage
    peak_mem_overall = mx.metal.get_peak_memory() / 1024**3

    # Report memory usage
    if verbose:
        print(f"Peak memory used for unet: {peak_mem_unet:.3f}GB")
        print(f"Peak memory used overall: {peak_mem_overall:.3f}GB")

    # Clean up
    image_gen.close()

    return output


def test_image2image(
    prompt="A lit fireplace",
    model="sdxl",
    strength=0.5,
    local_model_path="",
    n_images=1,
    steps=None,
    cfg=None,
    negative_prompt="",
    n_rows=1,
    decoding_batch_size=1,
    quantize=False,
    float16=True,
    preload_models=False,
    init_image_path="out_txt2img.png",
    output="out_img2img.png",
    verbose=False,
    seed=None,
    width=256,
    height=256,
):
    """Generate images from image and text prompt using high-level interface"""

    # Determine model path based on model type
    if model == "sdxl":
        model_path = local_model_path or "stabilityai/sdxl-turbo"
        default_cfg = 0.0
        default_steps = 2
    else:
        model_path = local_model_path or "stabilityai/stable-diffusion-2-1-base"
        default_cfg = 7.5
        default_steps = 50

    # Use provided values or defaults
    cfg = cfg or default_cfg
    steps = steps or default_steps

    # Load and process input image
    try:
        pil_img = PILImage.open(init_image_path)
        # Ensure RGB format
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")

        # Convert to numpy array and then to our Image class
        img_np = np.array(pil_img).astype(np.float32) / 255.0  # Normalize to [0,1]
        init_image = Image.from_numpy(img_np)

    except FileNotFoundError:
        print(f"Error: Image file '{init_image_path}' not found.")
        return None
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

    # Create ImageGen instance
    image_gen = ImageGen(model_path, "", device=None)

    # Load the model
    if not image_gen.load_model(model_path):
        print(f"Failed to load model: {model_path}")
        return None

    # Create sampler configuration
    sampler_config = ImageSamplerConfig(
        method="ddim",
        steps=steps,
        guidance_scale=cfg,
        seed=seed if seed is not None else -1,
    )

    # Create generation configuration
    gen_config = ImageGenerationConfig(
        prompts=prompt,
        negative_prompts=negative_prompt,
        height=height,
        width=width,
        sampler_config=sampler_config,
        init_image=init_image,
        strength=strength,
    )

    if verbose:
        print(f"Generating image with prompt: '{prompt}' and strength: {strength}")
        print(f"Model: {model_path}, Steps: {steps}, CFG: {cfg}")

    # Generate image using img2img
    result_image = image_gen.img2img(init_image, prompt, gen_config)

    # Free memory by deleting model components (following main_duplicate.py pattern)
    if image_gen.model:
        if model == "sdxl":
            if hasattr(image_gen.model, "text_encoder_1"):
                del image_gen.model.text_encoder_1
            if hasattr(image_gen.model, "text_encoder_2"):
                del image_gen.model.text_encoder_2
        else:
            if hasattr(image_gen.model, "text_encoder"):
                del image_gen.model.text_encoder

        if hasattr(image_gen.model, "unet"):
            del image_gen.model.unet
        if hasattr(image_gen.model, "sampler"):
            del image_gen.model.sampler

    # Get peak memory usage
    peak_mem_unet = mx.metal.get_peak_memory() / 1024**3

    # Convert to PIL and save
    image_np = result_image.to_numpy()
    image_pil = PILImage.fromarray((image_np * 255).astype(np.uint8))
    image_pil.save(output)

    print(f"Image-to-image output saved to: {output}")

    # Get final peak memory usage
    peak_mem_overall = mx.metal.get_peak_memory() / 1024**3

    # Report memory usage
    if verbose:
        print(f"Peak memory used for unet: {peak_mem_unet:.3f}GB")
        print(f"Peak memory used overall: {peak_mem_overall:.3f}GB")

    # Clean up
    image_gen.close()

    return output


if __name__ == "__main__":
    # Text-to-image parameters
    txt2img_params = {
        "prompt": "A photo of an astronaut riding a horse on Mars.",
        "model": "sdxl",
        "n_images": 1,
        "n_rows": 1,
        "output": "out_txt2img.png",
        "verbose": True,
        "width": 256,
        "height": 256,
    }

    # Image-to-image parameters
    img2img_params = {
        "prompt": "A lit fireplace",
        "model": "sdxl",
        "strength": 0.5,
        "n_images": 1,
        "n_rows": 1,
        "init_image_path": "out_txt2img.png",
        "output": "out_img2img.png",
        "verbose": True,
        "width": 512,
        "height": 512,
    }

    print("Running text-to-image generation...")
    generated_image = test_txt2image(**txt2img_params)

    if generated_image:
        print(f"\nRunning image-to-image generation using: {generated_image}")
        img2img_params["init_image_path"] = generated_image
        test_image2image(**img2img_params)

        print(f"\nPipeline complete!")
        print(f"Text-to-image result: {txt2img_params['output']}")
        print(f"Image-to-image result: {img2img_params['output']}")
    else:
        print("Failed to generate initial image, skipping img2img test")
