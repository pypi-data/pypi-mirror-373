#!/usr/bin/env python3

import os
import sys
import time
import math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .modeling.pp_ocr_v4 import Config, TextSystem


def is_image_file(file_path):
    """Check if file is an image based on extension."""
    img_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".gif", ".rgb"}
    return Path(file_path).suffix.lower() in img_extensions


def get_image_file_list(img_file):
    """Get list of image files from a directory or single file."""
    imgs_lists = []
    if img_file is None or not os.path.exists(img_file):
        raise Exception("not found any img file in {}".format(img_file))

    if os.path.isfile(img_file) and is_image_file(img_file):
        imgs_lists.append(img_file)
    elif os.path.isdir(img_file):
        for single_file in os.listdir(img_file):
            file_path = os.path.join(img_file, single_file)
            if is_image_file(file_path):
                imgs_lists.append(file_path)
    if len(imgs_lists) == 0:
        raise Exception("not found any img file in {}".format(img_file))
    return imgs_lists


def check_and_read_gif(img_path):
    """Check if image is gif and read it properly."""
    if os.path.basename(img_path)[-3:] in ["gif", "GIF"]:
        gif = cv2.VideoCapture(img_path)
        ret, frame = gif.read()
        if not ret:
            print("Cannot read {}. This gif image maybe corrupted.".format(img_path))
            return None, False
        if len(frame.shape) == 2 or frame.shape[-1] == 1:
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
        imgvalue = frame[:, :, ::-1]
        return imgvalue, True
    return None, False


def draw_ocr_box_txt(
    image, boxes, txts, scores=None, drop_score=0.5, font_path="./doc/simfang.ttf"
):
    """Draw OCR results with boxes and text."""
    h, w = image.height, image.width
    img_left = image.copy()
    img_right = Image.new("RGB", (w, h), (255, 255, 255))

    import random
    random.seed(0)

    draw_left = ImageDraw.Draw(img_left)
    draw_right = ImageDraw.Draw(img_right)

    for idx, (box, txt) in enumerate(zip(boxes, txts)):
        if scores is not None and scores[idx] < drop_score:
            continue

        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        draw_left.polygon(box, fill=color)
        draw_right.polygon(
            [
                box[0][0],
                box[0][1],
                box[1][0],
                box[1][1],
                box[2][0],
                box[2][1],
                box[3][0],
                box[3][1],
            ],
            outline=color,
        )

        box_height = math.sqrt((box[0][0] - box[3][0]) ** 2 + (box[0][1] - box[3][1]) ** 2)
        box_width = math.sqrt((box[0][0] - box[1][0]) ** 2 + (box[0][1] - box[1][1]) ** 2)

        if box_height > 2 * box_width:
            font_size = max(int(box_width * 0.9), 10)
            try:
                font = ImageFont.truetype(font_path, font_size, encoding="utf-8")
            except:
                font = ImageFont.load_default()
            cur_y = box[0][1]
            for c in txt:
                try:
                    bbox = font.getbbox(c)
                    char_size = (bbox[2] - bbox[0], bbox[3] - bbox[1])
                except:
                    char_size = (font_size, font_size)
                draw_right.text((box[0][0] + 3, cur_y), c, fill=(0, 0, 0), font=font)
                cur_y += char_size[1]
        else:
            font_size = max(int(box_height * 0.8), 10)
            try:
                font = ImageFont.truetype(font_path, font_size, encoding="utf-8")
            except:
                font = ImageFont.load_default()
            draw_right.text([box[0][0], box[0][1]], txt, fill=(0, 0, 0), font=font)

    img_left = Image.blend(image, img_left, 0.5)
    img_show = Image.new("RGB", (w * 2, h), (255, 255, 255))
    img_show.paste(img_left, (0, 0, w, h))
    img_show.paste(img_right, (w, 0, w * 2, h))

    return np.array(img_show)


def load_model():
    """Load OCR model and return config and text system."""
    config = Config()
    ocr_system = TextSystem(config)
    return config, ocr_system


def process_folder(config, ocr_system):
    """Process all images in the configured folder."""
    img_paths = get_image_file_list(config.image_dir)
    if not img_paths:
        print("[ERR] No images found in", config.image_dir)
        return

    out_root = Path(config.base_dir) / "output"
    txt_dir = out_root / "inference_txt"
    vis_dir = out_root / "inference_results"
    txt_dir.mkdir(parents=True, exist_ok=True)
    vis_dir.mkdir(parents=True, exist_ok=True)

    font = config.vis_font_path

    total = 0.0
    for idx, p in enumerate(img_paths, 1):
        img, is_gif = check_and_read_gif(p)
        if not is_gif:
            img = cv2.imread(p)
        if img is None:
            print(f"[WARN] skip {p}")
            continue

        t0 = time.time()
        boxes, recs = ocr_system(img)
        dt = time.time() - t0
        total += dt

        name = Path(p).stem

        with open(txt_dir / f"{name}.txt", "w", encoding="utf-8") as f:
            f.writelines(f"{txt}\n" for txt, sc in recs) # DO NOT write confidence score in txt file

        vis = draw_ocr_box_txt(
            Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)),
            boxes,
            [t for t, _ in recs],
            [s for _, s in recs],
            drop_score=config.drop_score,
            font_path=font,
        )
        cv2.imwrite(str(vis_dir / f"{name}.jpg"), vis[:, :, ::-1])

        print(f"[{idx}/{len(img_paths)}] {Path(p).name}  boxes={len(boxes)}  time={dt:.3f}s")

    print(f"\nDone {len(img_paths)} images in {total:.2f}s  (avg {total/len(img_paths):.3f}s)")


def main():
    """Main function to demonstrate OCR functionality."""
    print("📥 Loading OCR model...")
    
    # Load model and config
    config, ocr_system = load_model()
    
    print("✅ OCR model loaded successfully!")
    print(f"📂 Processing images from: {config.image_dir}")
    print("="*50)
    
    # Process images
    process_folder(config, ocr_system)


if __name__ == "__main__":
    main()
