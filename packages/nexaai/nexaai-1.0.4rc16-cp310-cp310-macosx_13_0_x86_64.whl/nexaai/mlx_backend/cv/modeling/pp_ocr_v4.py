#!/usr/bin/env python3

import sys
import time
import os
import shutil
import math
from pathlib import Path
from typing import List, Tuple
import cv2
import numpy as np
from PIL import Image
from shapely.geometry import Polygon
import pyclipper

import mlx.core as mx
import mlx.nn as nn

## =============================== PREPROCESSING CLASSES =============================== #


class DetResizeForTest(object):
    def __init__(self, **kwargs):
        super(DetResizeForTest, self).__init__()
        self.resize_type = 0
        if "image_shape" in kwargs:
            self.image_shape = kwargs["image_shape"]
            self.resize_type = 1
        elif "limit_side_len" in kwargs:
            self.limit_side_len = kwargs["limit_side_len"]
            self.limit_type = kwargs.get("limit_type", "min")
        elif "resize_long" in kwargs:
            self.resize_type = 2
            self.resize_long = kwargs.get("resize_long", 960)
        else:
            self.limit_side_len = 736
            self.limit_type = "min"

    def __call__(self, data):
        img = data["image"]
        src_h, src_w, _ = img.shape

        if self.resize_type == 0:
            img, [ratio_h, ratio_w] = self.resize_image_type0(img)
        elif self.resize_type == 2:
            img, [ratio_h, ratio_w] = self.resize_image_type2(img)
        else:
            img, [ratio_h, ratio_w] = self.resize_image_type1(img)
        data["image"] = img
        data["shape"] = np.array([src_h, src_w, ratio_h, ratio_w])
        return data

    def resize_image_type1(self, img):
        resize_h, resize_w = self.image_shape
        ori_h, ori_w = img.shape[:2]
        ratio_h = float(resize_h) / ori_h
        ratio_w = float(resize_w) / ori_w
        img = cv2.resize(img, (int(resize_w), int(resize_h)))
        return img, [ratio_h, ratio_w]

    def resize_image_type0(self, img):
        limit_side_len = self.limit_side_len
        h, w, c = img.shape

        if self.limit_type == "max":
            if max(h, w) > limit_side_len:
                if h > w:
                    ratio = float(limit_side_len) / h
                else:
                    ratio = float(limit_side_len) / w
            else:
                ratio = 1.0
        elif self.limit_type == "min":
            if min(h, w) < limit_side_len:
                if h < w:
                    ratio = float(limit_side_len) / h
                else:
                    ratio = float(limit_side_len) / w
            else:
                ratio = 1.0
        elif self.limit_type == "resize_long":
            ratio = float(limit_side_len) / max(h, w)
        else:
            raise Exception("not support limit type, image ")
        resize_h = int(h * ratio)
        resize_w = int(w * ratio)

        resize_h = max(int(round(resize_h / 32) * 32), 32)
        resize_w = max(int(round(resize_w / 32) * 32), 32)

        try:
            if int(resize_w) <= 0 or int(resize_h) <= 0:
                return None, (None, None)
            img = cv2.resize(img, (int(resize_w), int(resize_h)))
        except:
            print(img.shape, resize_w, resize_h)
            sys.exit(0)
        ratio_h = resize_h / float(h)
        ratio_w = resize_w / float(w)
        return img, [ratio_h, ratio_w]

    def resize_image_type2(self, img):
        h, w, _ = img.shape
        resize_w = w
        resize_h = h

        if resize_h > resize_w:
            ratio = float(self.resize_long) / resize_h
        else:
            ratio = float(self.resize_long) / resize_w

        resize_h = int(resize_h * ratio)
        resize_w = int(resize_w * ratio)

        max_stride = 128
        resize_h = (resize_h + max_stride - 1) // max_stride * max_stride
        resize_w = (resize_w + max_stride - 1) // max_stride * max_stride
        img = cv2.resize(img, (int(resize_w), int(resize_h)))
        ratio_h = resize_h / float(h)
        ratio_w = resize_w / float(w)

        return img, [ratio_h, ratio_w]


class NormalizeImage(object):
    def __init__(self, scale=None, mean=None, std=None, order="chw", **kwargs):
        if isinstance(scale, str):
            scale = eval(scale)
        self.scale = np.float32(scale if scale is not None else 1.0 / 255.0)
        mean = mean if mean is not None else [0.485, 0.456, 0.406]
        std = std if std is not None else [0.229, 0.224, 0.225]

        shape = (3, 1, 1) if order == "chw" else (1, 1, 3)
        self.mean = np.array(mean).reshape(shape).astype("float32")
        self.std = np.array(std).reshape(shape).astype("float32")

    def __call__(self, data):
        img = data["image"]
        from PIL import Image

        if isinstance(img, Image.Image):
            img = np.array(img)
        assert isinstance(img, np.ndarray), "invalid input 'img' in NormalizeImage"
        data["image"] = (img.astype("float32") * self.scale - self.mean) / self.std
        return data


class ToCHWImage(object):
    def __init__(self, **kwargs):
        pass

    def __call__(self, data):
        img = data["image"]
        from PIL import Image

        if isinstance(img, Image.Image):
            img = np.array(img)
        data["image"] = img.transpose((2, 0, 1))
        return data


class KeepKeys(object):
    def __init__(self, keep_keys, **kwargs):
        self.keep_keys = keep_keys

    def __call__(self, data):
        data_list = []
        for key in self.keep_keys:
            data_list.append(data[key])
        return data_list


## =============================== POSTPROCESSING CLASSES =============================== #


class DBPostProcess(object):
    def __init__(
        self,
        thresh=0.3,
        box_thresh=0.7,
        max_candidates=1000,
        unclip_ratio=2.0,
        use_dilation=False,
        score_mode="fast",
        **kwargs,
    ):
        self.thresh = thresh
        self.box_thresh = box_thresh
        self.max_candidates = max_candidates
        self.unclip_ratio = unclip_ratio
        self.min_size = 3
        self.score_mode = score_mode
        assert score_mode in [
            "slow",
            "fast",
        ], "Score mode must be in [slow, fast] but got: {}".format(score_mode)
        self.dilation_kernel = None if not use_dilation else np.array([[1, 1], [1, 1]])

    def boxes_from_bitmap(self, pred, _bitmap, dest_width, dest_height):
        bitmap = _bitmap
        height, width = bitmap.shape

        outs = cv2.findContours(
            (bitmap * 255).astype(np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
        )
        if len(outs) == 3:
            img, contours, _ = outs[0], outs[1], outs[2]
        elif len(outs) == 2:
            contours, _ = outs[0], outs[1]

        num_contours = min(len(contours), self.max_candidates)

        boxes = []
        scores = []
        for index in range(num_contours):
            contour = contours[index]
            points, sside = self.get_mini_boxes(contour)
            if sside < self.min_size:
                continue
            points = np.array(points)
            if self.score_mode == "fast":
                score = self.box_score_fast(pred, points.reshape(-1, 2))
            else:
                score = self.box_score_slow(pred, contour)
            if self.box_thresh > score:
                continue

            box = self.unclip(points).reshape(-1, 1, 2)
            box, sside = self.get_mini_boxes(box)
            if sside < self.min_size + 2:
                continue
            box = np.array(box)

            box[:, 0] = np.clip(np.round(box[:, 0] / width * dest_width), 0, dest_width)
            box[:, 1] = np.clip(np.round(box[:, 1] / height * dest_height), 0, dest_height)
            boxes.append(box.astype(np.int16))
            scores.append(score)
        return np.array(boxes, dtype=np.int16), scores

    def unclip(self, box):
        unclip_ratio = self.unclip_ratio
        poly = Polygon(box)
        distance = poly.area * unclip_ratio / poly.length
        offset = pyclipper.PyclipperOffset()
        offset.AddPath(box, pyclipper.JT_ROUND, pyclipper.ET_CLOSEDPOLYGON)
        expanded = np.array(offset.Execute(distance))
        return expanded

    def get_mini_boxes(self, contour):
        bounding_box = cv2.minAreaRect(contour)
        points = sorted(list(cv2.boxPoints(bounding_box)), key=lambda x: x[0])

        index_1, index_2, index_3, index_4 = 0, 1, 2, 3
        if points[1][1] > points[0][1]:
            index_1 = 0
            index_4 = 1
        else:
            index_1 = 1
            index_4 = 0
        if points[3][1] > points[2][1]:
            index_2 = 2
            index_3 = 3
        else:
            index_2 = 3
            index_3 = 2

        box = [points[index_1], points[index_2], points[index_3], points[index_4]]
        return box, min(bounding_box[1])

    def box_score_fast(self, bitmap, _box):
        h, w = bitmap.shape[:2]
        box = _box.copy()
        xmin = np.clip(np.floor(box[:, 0].min()).astype(int), 0, w - 1)
        xmax = np.clip(np.ceil(box[:, 0].max()).astype(int), 0, w - 1)
        ymin = np.clip(np.floor(box[:, 1].min()).astype(int), 0, h - 1)
        ymax = np.clip(np.ceil(box[:, 1].max()).astype(int), 0, h - 1)

        mask = np.zeros((ymax - ymin + 1, xmax - xmin + 1), dtype=np.uint8)
        box[:, 0] = box[:, 0] - xmin
        box[:, 1] = box[:, 1] - ymin
        cv2.fillPoly(mask, box.reshape(1, -1, 2).astype(np.int32), 1)
        return cv2.mean(bitmap[ymin : ymax + 1, xmin : xmax + 1], mask)[0]

    def box_score_slow(self, bitmap, contour):
        h, w = bitmap.shape[:2]
        contour = contour.copy()
        contour = np.reshape(contour, (-1, 2))

        xmin = np.clip(np.min(contour[:, 0]), 0, w - 1)
        xmax = np.clip(np.max(contour[:, 0]), 0, w - 1)
        ymin = np.clip(np.min(contour[:, 1]), 0, h - 1)
        ymax = np.clip(np.max(contour[:, 1]), 0, h - 1)

        mask = np.zeros((ymax - ymin + 1, xmax - xmin + 1), dtype=np.uint8)
        contour[:, 0] = contour[:, 0] - xmin
        contour[:, 1] = contour[:, 1] - ymin
        cv2.fillPoly(mask, contour.reshape(1, -1, 2).astype(np.int32), 1)
        return cv2.mean(bitmap[ymin : ymax + 1, xmin : xmax + 1], mask)[0]

    def __call__(self, outs_dict, shape_list):
        pred = outs_dict["maps"]
        if hasattr(pred, "numpy"):  # Check if it has numpy method (for torch tensors)
            pred = pred.numpy()
        elif isinstance(pred, mx.array):  # For MLX arrays
            pred = np.array(pred)
        pred = pred[:, 0, :, :]
        segmentation = pred > self.thresh

        boxes_batch = []
        for batch_index in range(pred.shape[0]):
            src_h, src_w, ratio_h, ratio_w = shape_list[batch_index]
            if self.dilation_kernel is not None:
                mask = cv2.dilate(
                    np.array(segmentation[batch_index]).astype(np.uint8), self.dilation_kernel
                )
            else:
                mask = segmentation[batch_index]
            boxes, scores = self.boxes_from_bitmap(pred[batch_index], mask, src_w, src_h)
            boxes_batch.append({"points": boxes})
        return boxes_batch


class BaseRecLabelDecode(object):
    def __init__(self, character_dict_path=None, use_space_char=False):
        self.beg_str = "sos"
        self.end_str = "eos"
        self.character_str = []
        if character_dict_path is None:
            self.character_str = "0123456789abcdefghijklmnopqrstuvwxyz"
            dict_character = list(self.character_str)
        else:
            with open(character_dict_path, "rb") as fin:
                lines = fin.readlines()
                for line in lines:
                    line = line.decode("utf-8").strip("\n").strip("\r\n")
                    self.character_str.append(line)
            if use_space_char:
                self.character_str.append(" ")
            dict_character = list(self.character_str)

        dict_character = self.add_special_char(dict_character)
        self.dict = {}
        for i, char in enumerate(dict_character):
            self.dict[char] = i
        self.character = dict_character

    def add_special_char(self, dict_character):
        return dict_character

    def decode(self, text_index, text_prob=None, is_remove_duplicate=False):
        result_list = []
        ignored_tokens = self.get_ignored_tokens()
        batch_size = len(text_index)
        for batch_idx in range(batch_size):
            char_list = []
            conf_list = []
            for idx in range(len(text_index[batch_idx])):
                if text_index[batch_idx][idx] in ignored_tokens:
                    continue
                if is_remove_duplicate:
                    if idx > 0 and text_index[batch_idx][idx - 1] == text_index[batch_idx][idx]:
                        continue
                char_list.append(self.character[int(text_index[batch_idx][idx])])
                if text_prob is not None:
                    conf_list.append(text_prob[batch_idx][idx])
                else:
                    conf_list.append(1)
            text = "".join(char_list)
            # Check if conf_list is empty before calculating mean
            confidence = np.mean(conf_list) if len(conf_list) > 0 else 0.0
            result_list.append((text, confidence))
        return result_list

    def get_ignored_tokens(self):
        return [0]


class CTCLabelDecode(BaseRecLabelDecode):
    def __init__(self, character_dict_path=None, use_space_char=False, **kwargs):
        super(CTCLabelDecode, self).__init__(character_dict_path, use_space_char)

    def __call__(self, preds, label=None, *args, **kwargs):
        if hasattr(preds, "numpy"):  # Check if it has numpy method (for torch tensors)
            preds = preds.numpy()
        elif isinstance(preds, mx.array):  # For MLX arrays
            preds = np.array(preds)
        preds_idx = preds.argmax(axis=2)
        preds_prob = preds.max(axis=2)
        text = self.decode(preds_idx, preds_prob, is_remove_duplicate=True)

        if label is None:
            return text
        label = self.decode(label)
        return text, label

    def add_special_char(self, dict_character):
        dict_character = ["blank"] + dict_character
        return dict_character


## =============================== CONFIG CLASS =============================== #


class Config:
    def __init__(self, model_path):
        # Base paths
        self.base_dir = os.path.abspath(os.path.dirname(__file__))
        
        self.model_cache_dir = model_path

        # Detection settings
        self.det_algorithm = "DB"
        # Use downloaded model files instead of local paths
        self.det_model_path = os.path.join(
            self.model_cache_dir, "ch_ptocr_v4_det_infer.safetensors"
        )
        self.det_limit_side_len = 960
        self.det_limit_type = "max"
        self.det_db_thresh = 0.3
        self.det_db_box_thresh = 0.6
        self.det_db_unclip_ratio = 1.5
        self.use_dilation = False
        self.det_db_score_mode = "fast"

        # Recognition settings
        self.rec_algorithm = "CRNN"
        # Use downloaded model files instead of local paths
        self.rec_model_path = os.path.join(
            self.model_cache_dir, "ch_ptocr_v4_rec_infer_f16.safetensors"
        )
        self.rec_char_type = "ch"
        self.rec_batch_num = 6
        self.max_text_length = 25
        # Use downloaded character dictionary
        self.rec_char_dict_path = os.path.join(self.model_cache_dir, "ppocr_keys_v1.txt")

        # Other settings
        self.use_space_char = True
        self.drop_score = 0.5
        self.limited_max_width = 1280
        self.limited_min_width = 16
        # Use downloaded font file
        self.vis_font_path = os.path.join(self.model_cache_dir, "simfang.ttf")


## =============================== MODEL COMPONENTS =============================== #


class LearnableAffineBlock(nn.Module):
    def __init__(self, scale_value=1.0, bias_value=0.0, lr_mult=1.0, lab_lr=0.1):
        super().__init__()
        # Match PyTorch parameter names exactly (lr_mult and lab_lr are ignored in MLX)
        self.scale = mx.array([scale_value])
        self.bias = mx.array([bias_value])

    def __call__(self, x):
        return self.scale * x + self.bias


class ConvBNLayer(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, stride, groups=1, lr_mult=1.0):
        super().__init__()
        # lr_mult is ignored in MLX - it's a PyTorch/PaddlePaddle concept
        padding = (kernel_size - 1) // 2
        self.conv = nn.Conv2d(
            in_channels, out_channels, kernel_size, stride, padding, groups=groups, bias=False
        )
        self.bn = nn.BatchNorm(out_channels)

    def __call__(self, x):
        x = self.conv(x)
        x = self.bn(x)
        return x


class Act(nn.Module):
    def __init__(self, act="hswish", lr_mult=1.0, lab_lr=0.1):
        super().__init__()
        # lr_mult and lab_lr are ignored in MLX
        self.lab = LearnableAffineBlock(lr_mult=lr_mult, lab_lr=lab_lr)

    def __call__(self, x):
        return self.lab(nn.hardswish(x))


class LearnableRepLayer(nn.Module):
    def __init__(
        self,
        in_channels,
        out_channels,
        kernel_size,
        stride=1,
        groups=1,
        num_conv_branches=4,
        lr_mult=1.0,
        lab_lr=0.1,
    ):
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.stride = stride
        self.groups = groups
        self.num_conv_branches = num_conv_branches

        # Identity connection - only if channels match and stride is 1
        self.identity = None
        if out_channels == in_channels and stride == 1:
            self.identity = nn.BatchNorm(in_channels)

        # Create main conv branches using a list to match PyTorch structure
        self.conv_kxk = []
        for _ in range(num_conv_branches):
            conv = ConvBNLayer(
                in_channels, out_channels, kernel_size, stride, groups=groups, lr_mult=lr_mult
            )
            self.conv_kxk.append(conv)

        # 1x1 conv branch - only if kernel > 1
        self.conv_1x1 = None
        if kernel_size > 1:
            self.conv_1x1 = ConvBNLayer(
                in_channels, out_channels, 1, stride, groups=groups, lr_mult=lr_mult
            )

        self.lab = LearnableAffineBlock(lr_mult=lr_mult, lab_lr=lab_lr)
        self.act = Act(lr_mult=lr_mult, lab_lr=lab_lr)

    def __call__(self, x):
        out = 0

        # Add identity if available
        if self.identity is not None:
            out = out + self.identity(x)

        # Add 1x1 conv if available
        if self.conv_1x1 is not None:
            out = out + self.conv_1x1(x)

        # Add all conv_kxk branches
        for conv in self.conv_kxk:
            out = out + conv(x)

        # Apply learnable affine and activation
        out = self.lab(out)
        if self.stride != 2:
            out = self.act(out)

        return out


class SELayer(nn.Module):
    def __init__(self, channel, reduction=4, lr_mult=1.0):
        super().__init__()
        # lr_mult is ignored in MLX
        reduced_channels = max(1, channel // reduction)
        self.conv1 = nn.Conv2d(channel, reduced_channels, 1)
        self.conv2 = nn.Conv2d(reduced_channels, channel, 1)

    def __call__(self, x):
        identity = x
        se_input = mx.mean(x, axis=(1, 2), keepdims=True)  # Changed from (2, 3) to (1, 2)
        se_out = nn.relu(self.conv1(se_input))
        se_out = self.conv2(se_out)
        se_out = mx.clip(se_out + 3.0, 0.0, 6.0) / 6.0
        se_out = identity * se_out
        return se_out


class LCNetV3Block(nn.Module):
    def __init__(
        self,
        in_channels,
        out_channels,
        stride,
        dw_size,
        use_se=False,
        conv_kxk_num=4,
        lr_mult=1.0,
        lab_lr=0.1,
    ):
        super().__init__()
        self.use_se = use_se

        # Depthwise convolution: in_channels -> in_channels with groups=in_channels
        self.dw_conv = LearnableRepLayer(
            in_channels=in_channels,  # INPUT: 192
            out_channels=in_channels,  # OUTPUT: 192 (same as input for depthwise)
            kernel_size=dw_size,
            stride=stride,
            groups=in_channels,  # GROUPS: 192 (depthwise)
            num_conv_branches=conv_kxk_num,
            lr_mult=lr_mult,
            lab_lr=lab_lr,
        )

        if use_se:
            self.se = SELayer(in_channels, lr_mult=lr_mult)

        # Pointwise convolution: in_channels -> out_channels with groups=1
        self.pw_conv = LearnableRepLayer(
            in_channels=in_channels,  # INPUT: 192
            out_channels=out_channels,  # OUTPUT: 384
            kernel_size=1,
            stride=1,
            groups=1,  # GROUPS: 1 (pointwise)
            num_conv_branches=conv_kxk_num,
            lr_mult=lr_mult,
            lab_lr=lab_lr,
        )

    def __call__(self, x):
        x = self.dw_conv(x)
        if self.use_se:
            x = self.se(x)
        x = self.pw_conv(x)
        return x


def make_divisible(v, divisor=16):
    return max(divisor, int(v + divisor / 2) // divisor * divisor)


# Add the NET_CONFIG_det at the top
NET_CONFIG_det = {
    "blocks2": [[3, 16, 32, 1, False]],
    "blocks3": [[3, 32, 64, 2, False], [3, 64, 64, 1, False]],
    "blocks4": [[3, 64, 128, 2, False], [3, 128, 128, 1, False]],
    "blocks5": [
        [3, 128, 256, 2, False],
        [5, 256, 256, 1, False],
        [5, 256, 256, 1, False],
        [5, 256, 256, 1, False],
        [5, 256, 256, 1, False],
    ],
    "blocks6": [
        [5, 256, 512, 2, True],
        [5, 512, 512, 1, True],
        [5, 512, 512, 1, False],
        [5, 512, 512, 1, False],
    ],
}

NET_CONFIG_rec = {
    "blocks2": [[3, 16, 32, 1, False]],
    "blocks3": [[3, 32, 64, 1, False], [3, 64, 64, 1, False]],
    "blocks4": [[3, 64, 128, (2, 1), False], [3, 128, 128, 1, False]],
    "blocks5": [
        [3, 128, 256, (1, 2), False],
        [5, 256, 256, 1, False],
        [5, 256, 256, 1, False],
        [5, 256, 256, 1, False],
        [5, 256, 256, 1, False],
    ],
    "blocks6": [
        [5, 256, 512, (2, 1), True],
        [5, 512, 512, 1, True],
        [5, 512, 512, (2, 1), False],
        [5, 512, 512, 1, False],
    ],
}


## ===================================  for the backbone of text recognition ===================================
class PPLCNetV3(nn.Module):
    def __init__(
        self,
        scale=1.0,
        conv_kxk_num=4,
        lr_mult_list=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        lab_lr=0.1,
        det=False,
        **kwargs,
    ):
        super().__init__()
        self.scale = scale
        self.lr_mult_list = lr_mult_list
        self.det = det
        self.net_config = NET_CONFIG_det if self.det else NET_CONFIG_rec

        assert isinstance(self.lr_mult_list, (list, tuple))
        assert len(self.lr_mult_list) == 6

        self.conv1 = ConvBNLayer(
            in_channels=3,
            out_channels=make_divisible(16 * scale),
            kernel_size=3,
            stride=2,
            lr_mult=self.lr_mult_list[0],
        )

        # Build blocks2 - match PyTorch Sequential structure
        blocks2_list = []
        in_channels = make_divisible(16 * scale)
        for i, (k, _, out_c, s, se) in enumerate(self.net_config["blocks2"]):
            out_channels = make_divisible(out_c * scale)
            block = LCNetV3Block(
                in_channels=in_channels,
                out_channels=out_channels,
                dw_size=k,
                stride=s,
                use_se=se,
                conv_kxk_num=conv_kxk_num,
                lr_mult=self.lr_mult_list[1],
                lab_lr=lab_lr,
            )
            blocks2_list.append(block)
            in_channels = out_channels
        self.blocks2 = blocks2_list

        # Build blocks3
        blocks3_list = []
        for i, (k, _, out_c, s, se) in enumerate(self.net_config["blocks3"]):
            out_channels = make_divisible(out_c * scale)
            block = LCNetV3Block(
                in_channels=in_channels,
                out_channels=out_channels,
                dw_size=k,
                stride=s,
                use_se=se,
                conv_kxk_num=conv_kxk_num,
                lr_mult=self.lr_mult_list[2],
                lab_lr=lab_lr,
            )
            blocks3_list.append(block)
            in_channels = out_channels
        self.blocks3 = blocks3_list

        # Build blocks4
        blocks4_list = []
        for i, (k, _, out_c, s, se) in enumerate(self.net_config["blocks4"]):
            out_channels = make_divisible(out_c * scale)
            block = LCNetV3Block(
                in_channels=in_channels,
                out_channels=out_channels,
                dw_size=k,
                stride=s,
                use_se=se,
                conv_kxk_num=conv_kxk_num,
                lr_mult=self.lr_mult_list[3],
                lab_lr=lab_lr,
            )
            blocks4_list.append(block)
            in_channels = out_channels
        self.blocks4 = blocks4_list

        # Build blocks5
        blocks5_list = []
        for i, (k, _, out_c, s, se) in enumerate(self.net_config["blocks5"]):
            out_channels = make_divisible(out_c * scale)
            block = LCNetV3Block(
                in_channels=in_channels,
                out_channels=out_channels,
                dw_size=k,
                stride=s,
                use_se=se,
                conv_kxk_num=conv_kxk_num,
                lr_mult=self.lr_mult_list[4],
                lab_lr=lab_lr,
            )
            blocks5_list.append(block)
            in_channels = out_channels
        self.blocks5 = blocks5_list

        # Build blocks6
        blocks6_list = []
        for i, (k, _, out_c, s, se) in enumerate(self.net_config["blocks6"]):
            out_channels = make_divisible(out_c * scale)
            block = LCNetV3Block(
                in_channels=in_channels,
                out_channels=out_channels,
                dw_size=k,
                stride=s,
                use_se=se,
                conv_kxk_num=conv_kxk_num,
                lr_mult=self.lr_mult_list[5],
                lab_lr=lab_lr,
            )
            blocks6_list.append(block)
            in_channels = out_channels
        self.blocks6 = blocks6_list

        self.out_channels = make_divisible(512 * scale)

        if self.det:
            mv_c = [16, 24, 56, 480]
            self.out_channels = [
                make_divisible(self.net_config["blocks3"][-1][2] * scale),
                make_divisible(self.net_config["blocks4"][-1][2] * scale),
                make_divisible(self.net_config["blocks5"][-1][2] * scale),
                make_divisible(self.net_config["blocks6"][-1][2] * scale),
            ]

            self.layer_list = []
            for i in range(4):
                layer = nn.Conv2d(self.out_channels[i], int(mv_c[i] * scale), 1, bias=True)
                self.layer_list.append(layer)

            self.out_channels = [
                int(mv_c[0] * scale),
                int(mv_c[1] * scale),
                int(mv_c[2] * scale),
                int(mv_c[3] * scale),
            ]

    def __call__(self, x):
        out_list = []

        ## Transpose to match the format required by MLX
        x = mx.transpose(x, (0, 2, 3, 1))
        x = self.conv1(x)

        for block in self.blocks2:
            x = block(x)

        for block in self.blocks3:
            x = block(x)
        out_list.append(x)

        for block in self.blocks4:
            x = block(x)
        out_list.append(x)

        for block in self.blocks5:
            x = block(x)
        out_list.append(x)

        for block in self.blocks6:
            x = block(x)
        out_list.append(x)

        if self.det:
            out_list[0] = self.layer_list[0](out_list[0])
            out_list[1] = self.layer_list[1](out_list[1])
            out_list[2] = self.layer_list[2](out_list[2])
            out_list[3] = self.layer_list[3](out_list[3])
            return out_list

        B, H, W, C = x.shape

        # Ensure dimensions are divisible by kernel size for clean pooling
        H_out = H // 3
        W_out = W // 2

        # Trim to make dimensions divisible
        x = x[:, : H_out * 3, : W_out * 2, :]

        # Reshape for 3x2 average pooling
        x = mx.reshape(x, (B, H_out, 3, W_out, 2, C))
        x = mx.mean(x, axis=(2, 4))  # Average over the 3x2 kernel
        return x


## ===================================  for the neck of text detection ===================================
class IndexedContainer(nn.Module):
    """Container that creates numbered attributes for MLX"""

    def __init__(self):
        super().__init__()
        self._modules = []

    def add_module(self, module):
        idx = len(self._modules)
        setattr(self, str(idx), module)
        self._modules.append(module)
        return idx

    def __getitem__(self, idx):
        return getattr(self, str(idx))


class SEModule(nn.Module):
    def __init__(self, in_channels, reduction=4):
        super().__init__()
        reduced_channels = in_channels // reduction
        self.conv1 = nn.Conv2d(in_channels, reduced_channels, 1, bias=True)
        self.conv2 = nn.Conv2d(reduced_channels, in_channels, 1, bias=True)

    def __call__(self, inputs):
        outputs = mx.mean(inputs, axis=(1, 2), keepdims=True)
        outputs = self.conv1(outputs)
        outputs = nn.relu(outputs)
        outputs = self.conv2(outputs)
        # PaddlePaddle hard_sigmoid: F.relu6(1.2 * x + 3.) / 6.
        outputs = mx.clip(1.2 * outputs + 3.0, 0.0, 6.0) / 6.0  # PaddlePaddle hard_sigmoid
        outputs = inputs * outputs
        return outputs


class RSELayer(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, shortcut=True):
        super().__init__()
        padding = kernel_size // 2
        self.in_conv = nn.Conv2d(
            in_channels, out_channels, kernel_size, padding=padding, bias=False
        )
        self.se_block = SEModule(out_channels)
        self.shortcut = shortcut

    def __call__(self, x):
        conv_out = self.in_conv(x)
        if self.shortcut:
            return conv_out + self.se_block(conv_out)
        else:
            return self.se_block(conv_out)


class RSEFPN(nn.Module):
    def __init__(self, in_channels, out_channels=96, shortcut=True):
        super().__init__()
        self.out_channels = out_channels

        # Create container modules that inherit from nn.Module
        self.ins_conv = IndexedContainer()
        self.inp_conv = IndexedContainer()

        # Add modules - this should create the correct parameter names
        for i, in_ch in enumerate(in_channels):
            self.ins_conv.add_module(
                RSELayer(in_ch, out_channels, kernel_size=1, shortcut=shortcut)
            )
            self.inp_conv.add_module(
                RSELayer(out_channels, out_channels // 4, kernel_size=3, shortcut=shortcut)
            )

    def __call__(self, x):
        c2, c3, c4, c5 = x

        in5 = self.ins_conv[3](c5)
        in4 = self.ins_conv[2](c4)
        in3 = self.ins_conv[1](c3)
        in2 = self.ins_conv[0](c2)

        # Upsample both H and W dimensions
        up_in5 = mx.repeat(in5, 2, axis=1)
        up_in5 = mx.repeat(up_in5, 2, axis=2)
        out4 = in4 + up_in5

        up_out4 = mx.repeat(out4, 2, axis=1)
        up_out4 = mx.repeat(up_out4, 2, axis=2)
        out3 = in3 + up_out4

        up_out3 = mx.repeat(out3, 2, axis=1)
        up_out3 = mx.repeat(up_out3, 2, axis=2)
        out2 = in2 + up_out3

        p5 = self.inp_conv[3](in5)
        p4 = self.inp_conv[2](out4)
        p3 = self.inp_conv[1](out3)
        p2 = self.inp_conv[0](out2)

        # Use target size from p2 for consistent upsampling
        target_h, target_w = p2.shape[1], p2.shape[2]

        # MLX doesn't have F.upsample, but we can calculate target sizes and use repeat more carefully
        # P5: upsample by 8x to match p2 size
        p5_h, p5_w = p5.shape[1], p5.shape[2]
        p5_target_h, p5_target_w = min(target_h, p5_h * 8), min(target_w, p5_w * 8)

        # Calculate exact repeat factors
        h_repeat_p5 = p5_target_h // p5_h
        w_repeat_p5 = p5_target_w // p5_w
        p5 = mx.repeat(p5, h_repeat_p5, axis=1)
        p5 = mx.repeat(p5, w_repeat_p5, axis=2)
        p5 = p5[:, :target_h, :target_w]

        # P4: upsample by 4x to match p2 size
        p4_h, p4_w = p4.shape[1], p4.shape[2]
        p4_target_h, p4_target_w = min(target_h, p4_h * 4), min(target_w, p4_w * 4)

        h_repeat_p4 = p4_target_h // p4_h
        w_repeat_p4 = p4_target_w // p4_w
        p4 = mx.repeat(p4, h_repeat_p4, axis=1)
        p4 = mx.repeat(p4, w_repeat_p4, axis=2)
        p4 = p4[:, :target_h, :target_w]

        # P3: upsample by 2x to match p2 size
        p3_h, p3_w = p3.shape[1], p3.shape[2]
        p3_target_h, p3_target_w = min(target_h, p3_h * 2), min(target_w, p3_w * 2)

        h_repeat_p3 = p3_target_h // p3_h
        w_repeat_p3 = p3_target_w // p3_w
        p3 = mx.repeat(p3, h_repeat_p3, axis=1)
        p3 = mx.repeat(p3, w_repeat_p3, axis=2)
        p3 = p3[:, :target_h, :target_w]

        fuse = mx.concatenate([p5, p4, p3, p2], axis=-1)
        return fuse


## ===================================  for the head of text detection ===================================
class DetectionHead(nn.Module):
    def __init__(self, in_channels):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels, in_channels // 4, 3, padding=1, bias=False)
        self.conv_bn1 = nn.BatchNorm(in_channels // 4)

        self.conv2 = nn.ConvTranspose2d(in_channels // 4, in_channels // 4, 2, stride=2)
        self.conv_bn2 = nn.BatchNorm(in_channels // 4)

        self.conv3 = nn.ConvTranspose2d(in_channels // 4, 1, 2, stride=2)

    def __call__(self, x):
        x = nn.relu(self.conv_bn1(self.conv1(x)))
        x = nn.relu(self.conv_bn2(self.conv2(x)))
        x = self.conv3(x)
        x = nn.sigmoid(x)
        return x


class DBHead(nn.Module):
    def __init__(self, in_channels, k=50):
        super().__init__()
        self.k = k
        self.binarize = DetectionHead(in_channels)  # First branch
        self.thresh = DetectionHead(in_channels)  # Second branch (was missing!)

    def step_function(self, x, y):
        return 1.0 / (1.0 + mx.exp(-self.k * (x - y)))

    def __call__(self, x):
        shrink_maps = self.binarize(x)
        shrink_maps = mx.transpose(shrink_maps, (0, 3, 1, 2))
        return {"maps": shrink_maps}


class TextDetector(nn.Module):
    def __init__(self, args):
        super().__init__()

        self.preprocess_op = [
            DetResizeForTest(
                limit_side_len=args.det_limit_side_len, limit_type=args.det_limit_type
            ),
            NormalizeImage(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
                scale=1.0 / 255.0,
                order="hwc",
            ),
            ToCHWImage(),
            KeepKeys(keep_keys=["image", "shape"]),
        ]

        postprocess_params = {
            "thresh": args.det_db_thresh,
            "box_thresh": args.det_db_box_thresh,
            "max_candidates": 1000,
            "unclip_ratio": args.det_db_unclip_ratio,
            "use_dilation": args.use_dilation,
            "score_mode": args.det_db_score_mode,
        }
        self.postprocess_op = DBPostProcess(**postprocess_params)

        # Match exact PyTorch model structure
        backbone_config = {"scale": 0.75, "det": True, "in_channels": 3}
        self.backbone = PPLCNetV3(**backbone_config)

        # Use correct neck config - the backbone outputs these channels
        neck_config = {
            "out_channels": 96,
            "shortcut": True,
            "in_channels": self.backbone.out_channels,  # Should be [12, 18, 42, 360]
        }
        self.neck = RSEFPN(**neck_config)

        head_config = {"k": 50, "in_channels": 96}
        self.head = DBHead(**head_config)

    def order_points_clockwise(self, pts):
        """
        reference from: https://github.com/jrosebr1/imutils/blob/master/imutils/perspective.py
        # sort the points based on their x-coordinates
        """
        xSorted = pts[np.argsort(pts[:, 0]), :]

        # grab the left-most and right-most points from the sorted
        # x-roodinate points
        leftMost = xSorted[:2, :]
        rightMost = xSorted[2:, :]

        # now, sort the left-most coordinates according to their
        # y-coordinates so we can grab the top-left and bottom-left
        # points, respectively
        leftMost = leftMost[np.argsort(leftMost[:, 1]), :]
        (tl, bl) = leftMost

        rightMost = rightMost[np.argsort(rightMost[:, 1]), :]
        (tr, br) = rightMost

        rect = np.array([tl, tr, br, bl], dtype="float32")
        return rect

    def clip_det_res(self, points, img_height, img_width):
        for pno in range(points.shape[0]):
            points[pno, 0] = int(min(max(points[pno, 0], 0), img_width - 1))
            points[pno, 1] = int(min(max(points[pno, 1], 0), img_height - 1))
        return points

    def filter_tag_det_res(self, dt_boxes, image_shape):
        img_height, img_width = image_shape[0:2]
        dt_boxes_new = []
        for box in dt_boxes:
            box = self.order_points_clockwise(box)
            box = self.clip_det_res(box, img_height, img_width)
            rect_width = int(np.linalg.norm(box[0] - box[1]))
            rect_height = int(np.linalg.norm(box[0] - box[3]))
            if rect_width <= 3 or rect_height <= 3:
                continue
            dt_boxes_new.append(box)
        return np.array(dt_boxes_new) if dt_boxes_new else np.array([])

    def forward(self, x):
        features = self.backbone(x)
        neck_out = self.neck(features)
        head_out = self.head(neck_out)
        return head_out

    def __call__(self, img):
        ori_im = img.copy()
        data = {"image": img}

        for op in self.preprocess_op:
            data = op(data)

        img, shape_list = data
        if img is None:
            return None, 0

        img = np.expand_dims(img, axis=0)
        shape_list = np.expand_dims(shape_list, axis=0)

        inp = mx.array(img.copy())
        outputs = self.forward(inp)
        preds = {"maps": np.array(outputs["maps"])}

        post_result = self.postprocess_op(preds, shape_list)
        dt_boxes = post_result[0]["points"] if post_result else []
        dt_boxes = self.filter_tag_det_res(dt_boxes, ori_im.shape)
        return dt_boxes


def test_detector(args):
    img = np.load(
        "/Users/alexchen/Desktop/LocalDev/nexaml-mlx/examples/paddle_ocr/modelfiles/det_inp.npy"
    )
    detector = TextDetector(args)
    detector.eval()
    detector.load_weights(
        "/Users/alexchen/Desktop/LocalDev/nexaml-mlx/examples/paddle_ocr/modelfiles/ch_ptocr_v4_det_infer.safetensors"
    )
    boxes = detector(img)
    print(f"Detected {len(boxes)} boxes")


## ==================================== Now the text det works ==================================== #


## ==================================== Text Recognition Components ==================================== #


class Im2Seq(nn.Module):
    def __init__(self, in_channels, **kwargs):
        super().__init__()
        self.out_channels = in_channels

    def __call__(self, x):
        B, H, W, C = x.shape  # MLX format: (B, H, W, C)
        assert H == 1
        x = mx.reshape(x, (B, H * W, C))  # (B, W, C) for sequence
        return x


class SVTRConvBNLayer(nn.Module):
    def __init__(
        self, in_channels, out_channels, kernel_size=3, stride=1, padding=0, groups=1, act="swish"
    ):
        super().__init__()
        self.conv = nn.Conv2d(
            in_channels, out_channels, kernel_size, stride, padding, groups=groups, bias=False
        )
        self.norm = nn.BatchNorm(out_channels)
        self.act = act

    def __call__(self, x):
        x = self.conv(x)
        x = self.norm(x)
        if self.act == "swish":
            x = x * mx.sigmoid(x)
        return x


class EncoderWithSVTR(nn.Module):
    def __init__(
        self,
        in_channels,
        dims=64,
        depth=2,
        hidden_dims=120,
        kernel_size=[3, 3],
        use_guide=False,
        **kwargs,
    ):
        super().__init__()
        self.depth = depth
        self.use_guide = use_guide

        # Match original PyTorch structure exactly
        self.conv1 = SVTRConvBNLayer(
            in_channels,
            in_channels // 8,
            kernel_size=(1, 3),  # Match actual model: (1, 3) not 3
            padding=(0, 1),  # Match actual model: (0, 1) not 1
            act="swish",
        )
        self.conv2 = SVTRConvBNLayer(
            in_channels // 8, hidden_dims, kernel_size=1, padding=0, act="swish"
        )

        # SVTR blocks - ADD THIS BACK!
        self.svtr_block = []
        for i in range(depth):
            block = Block(
                dim=hidden_dims,
                num_heads=8,
                mixer="Global",
                mlp_ratio=2.0,
                qkv_bias=True,  # Change from False to True
                act_layer="swish",  # Add this
                **kwargs,
            )
            setattr(self, f"svtr_block_{i}", block)
            self.svtr_block.append(block)

        self.norm = nn.LayerNorm(hidden_dims)

        self.conv3 = SVTRConvBNLayer(
            hidden_dims, in_channels, kernel_size=1, padding=0, act="swish"
        )
        self.conv4 = SVTRConvBNLayer(
            2 * in_channels, in_channels // 8, kernel_size=3, padding=1, act="swish"
        )
        self.conv1x1 = SVTRConvBNLayer(
            in_channels // 8, dims, kernel_size=1, padding=0, act="swish"
        )

        self.out_channels = dims

    def __call__(self, x):
        # Short cut
        h = x

        # Reduce dim
        z = self.conv1(x)
        z = self.conv2(z)

        # SVTR global blocks
        B, H, W, C = z.shape
        z = mx.reshape(z, (B, H * W, C))  # Flatten spatial dims

        for block in self.svtr_block:
            z = block(z)

        z = self.norm(z)

        # Reshape back - CRITICAL: use original H, W
        z = mx.reshape(z, (B, H, W, C))  # Use the H, W from before SVTR blocks
        z = self.conv3(z)

        # Concatenate with shortcut - dimensions should match now
        z = mx.concatenate([h, z], axis=-1)
        z = self.conv4(z)
        z = self.conv1x1(z)

        return z


class Mlp(nn.Module):
    def __init__(
        self, in_features, hidden_features=None, out_features=None, act_layer="swish", drop=0.0
    ):
        super().__init__()
        out_features = out_features or in_features
        hidden_features = hidden_features or in_features
        self.fc1 = nn.Linear(in_features, hidden_features, bias=True)  # Add bias=True
        self.fc2 = nn.Linear(hidden_features, out_features, bias=True)  # Add bias=True
        self.act_layer = act_layer

    def __call__(self, x):
        x = self.fc1(x)
        # Use swish activation to match PyTorch
        if self.act_layer == "swish":
            x = x * mx.sigmoid(x)  # Swish activation
        elif self.act_layer == "gelu":
            x = nn.gelu(x)
        x = self.fc2(x)
        return x


class Attention(nn.Module):
    def __init__(
        self,
        dim,
        num_heads=8,
        mixer="Global",
        HW=None,
        local_k=[7, 11],
        qkv_bias=False,
        qk_scale=None,
        attn_drop=0.0,
        proj_drop=0.0,
    ):
        super().__init__()
        self.num_heads = num_heads
        head_dim = dim // num_heads
        self.scale = qk_scale or head_dim**-0.5
        self.qkv = nn.Linear(dim, dim * 3, bias=qkv_bias)
        self.proj = nn.Linear(dim, dim, bias=True)
        self.attn_drop = nn.Dropout(attn_drop) if attn_drop > 0 else nn.Identity()
        self.proj_drop = nn.Dropout(proj_drop) if proj_drop > 0 else nn.Identity()
        self.HW = HW
        self.mixer = mixer

        # Set N and C if HW is provided (like in PyTorch)
        if HW is not None:
            H = HW[0]
            W = HW[1]
            self.N = H * W
            self.C = dim

    def __call__(self, x):
        if self.HW is not None:
            N = self.N
            C = self.C
        else:
            _, N, C = x.shape

        qkv = self.qkv(x)
        qkv = qkv.reshape((-1, N, 3, self.num_heads, C // self.num_heads))
        qkv = mx.transpose(qkv, (2, 0, 3, 1, 4))  # permute(2, 0, 3, 1, 4)
        q, k, v = qkv[0] * self.scale, qkv[1], qkv[2]

        attn = q @ mx.transpose(k, (0, 1, 3, 2))  # q.matmul(k.permute(0, 1, 3, 2))
        if self.mixer == "Local":
            # attn += self.mask  # Would need to implement mask for Local
            pass
        attn = mx.softmax(attn, axis=-1)  # nn.functional.softmax(attn, dim=-1)
        attn = self.attn_drop(attn)

        x = (attn @ v).transpose(0, 2, 1, 3).reshape((-1, N, C))  # Match exact reshape
        x = self.proj(x)
        x = self.proj_drop(x)
        return x


class Block(nn.Module):
    def __init__(
        self,
        dim,
        num_heads,
        mixer="Global",
        local_mixer=[7, 11],
        HW=None,
        mlp_ratio=4.0,
        qkv_bias=False,
        qk_scale=None,
        drop=0.0,
        attn_drop=0.0,
        drop_path=0.0,
        act_layer="gelu",
        norm_layer="nn.LayerNorm",
        epsilon=1e-6,
        prenorm=False,  # Set to False to match PyTorch
    ):
        super().__init__()
        self.norm1 = nn.LayerNorm(dim, eps=epsilon)
        self.mixer = Attention(
            dim,
            num_heads=num_heads,
            mixer=mixer,
            HW=HW,
            local_k=local_mixer,
            qkv_bias=qkv_bias,
            qk_scale=qk_scale,
            attn_drop=attn_drop,
            proj_drop=drop,
        )

        self.norm2 = nn.LayerNorm(dim, eps=epsilon)
        mlp_hidden_dim = int(dim * mlp_ratio)
        self.mlp = Mlp(
            in_features=dim, hidden_features=mlp_hidden_dim, act_layer=act_layer, drop=drop
        )
        self.prenorm = prenorm
        self.drop_path = drop_path

    def __call__(self, x):
        if self.prenorm:
            x = self.norm1(x + self._drop_path(self.mixer(x)))
            x = self.norm2(x + self._drop_path(self.mlp(x)))
        else:
            # This is the path that will be taken (prenorm=False)
            x = x + self._drop_path(self.mixer(self.norm1(x)))
            x = x + self._drop_path(self.mlp(self.norm2(x)))
        return x

    def _drop_path(self, x):
        # For inference, drop_path is disabled, so just return x
        return x


class SequenceEncoder(nn.Module):
    def __init__(self, in_channels, encoder_type="svtr", **kwargs):
        super().__init__()
        self.encoder_type = encoder_type.lower()
        self.encoder_reshape = Im2Seq(in_channels)

        if self.encoder_type == "svtr":
            self.encoder = EncoderWithSVTR(in_channels, **kwargs)
            self.out_channels = self.encoder.out_channels
            self.only_reshape = False
        else:
            self.out_channels = in_channels
            self.only_reshape = True

    def __call__(self, x):
        if self.encoder_type == "svtr":
            # For SVTR: encoder works on 2D data first, then reshape
            x = self.encoder(x)  # x is still (B, H, W, C)
            x = self.encoder_reshape(x)  # Now reshape to (B, W, C)
            return x
        else:
            # For others: reshape first, then encoder
            x = self.encoder_reshape(x)
            if not self.only_reshape:
                x = self.encoder(x)
            return x


class CTCHead(nn.Module):
    def __init__(
        self,
        in_channels,
        out_channels,
        fc_decay=0.0004,
        mid_channels=None,
        return_feats=False,
        **kwargs,
    ):
        super().__init__()
        self.return_feats = return_feats
        self.mid_channels = mid_channels

        if mid_channels is None:
            self.fc = nn.Linear(in_channels, out_channels, bias=True)
        else:
            self.fc1 = nn.Linear(in_channels, mid_channels, bias=True)
            self.fc2 = nn.Linear(mid_channels, out_channels, bias=True)

        self.out_channels = out_channels

    def __call__(self, x):
        if self.mid_channels is None:
            predicts = self.fc(x)
        else:
            x = self.fc1(x)
            predicts = self.fc2(x)

        if self.return_feats:
            result = (x, predicts)
        else:
            result = predicts

        # Apply softmax for inference using MLX
        if not self.training:
            predicts = mx.softmax(predicts, axis=2)
            result = predicts

        return result


class MultiHead(nn.Module):
    def __init__(self, in_channels, out_channels_list, head_list, **kwargs):
        super().__init__()
        self.head_list = head_list

        for idx, head_name in enumerate(self.head_list):
            name = list(head_name)[0]
            if name == "CTCHead":
                # No separate encoder_reshape - it's handled inside SequenceEncoder
                neck_args = self.head_list[idx][name]["Neck"].copy()
                encoder_type = neck_args.pop("name")
                self.ctc_encoder = SequenceEncoder(
                    in_channels=in_channels, encoder_type=encoder_type, **neck_args
                )
                # CTC head
                head_args = self.head_list[idx][name].get("Head", {})
                if head_args is None:
                    head_args = {}
                self.ctc_head = CTCHead(
                    in_channels=self.ctc_encoder.out_channels,
                    out_channels=out_channels_list["CTCLabelDecode"],
                    **head_args,
                )

    def __call__(self, x, data=None):
        # Direct call to ctc_encoder - let it handle reshaping internally
        ctc_encoder = self.ctc_encoder(x)
        ctc_out = self.ctc_head(ctc_encoder)

        # Eval mode
        if not self.training:
            return ctc_out

        head_out = dict()
        head_out["ctc"] = ctc_out
        head_out["res"] = ctc_out
        head_out["ctc_neck"] = ctc_encoder
        return head_out


class TextRecognizer(nn.Module):
    def __init__(self, args, **kwargs):
        super().__init__()

        self.rec_image_shape = [3, 48, 320]
        self.rec_batch_num = args.rec_batch_num
        self.limited_max_width = args.limited_max_width
        self.limited_min_width = args.limited_min_width

        # Character dictionary path
        postprocess_params = {
            "character_type": args.rec_char_type,
            "character_dict_path": args.rec_char_dict_path,
            "use_space_char": args.use_space_char,
        }
        self.postprocess_op = CTCLabelDecode(**postprocess_params)

        # Get character number
        char_num = len(getattr(self.postprocess_op, "character"))

        # Recognition backbone - reuse existing PPLCNetV3 (already handles transpose)
        self.backbone = PPLCNetV3(scale=0.95, det=False)

        # Recognition head
        head_config = {
            "head_list": [
                {
                    "CTCHead": {
                        "Neck": {
                            "name": "svtr",
                            "dims": 120,
                            "depth": 2,
                            "hidden_dims": 120,
                            "kernel_size": [1, 3],
                            "use_guide": True,
                        },
                        "Head": {"fc_decay": 1e-05},
                    }
                },
            ],
            "out_channels_list": {
                "CTCLabelDecode": char_num,
            },
            "in_channels": 480,  # PPLCNetV3 output channels
        }
        self.head = MultiHead(**head_config)

    def resize_norm_img(self, img, max_wh_ratio):
        imgC, imgH, imgW = self.rec_image_shape

        assert imgC == img.shape[2]
        max_wh_ratio = max(max_wh_ratio, imgW / imgH)
        imgW = int((imgH * max_wh_ratio))
        imgW = max(min(imgW, self.limited_max_width), self.limited_min_width)
        h, w = img.shape[:2]
        ratio = w / float(h)
        ratio_imgH = int(np.ceil(imgH * ratio))
        ratio_imgH = max(ratio_imgH, self.limited_min_width)
        if ratio_imgH > imgW:
            resized_w = imgW
        else:
            resized_w = int(ratio_imgH)

        resized_image = cv2.resize(img, (resized_w, imgH))
        resized_image = resized_image.astype("float32")
        resized_image = resized_image.transpose((2, 0, 1)) / 255
        resized_image -= 0.5
        resized_image /= 0.5
        padding_im = np.zeros((imgC, imgH, imgW), dtype=np.float32)
        padding_im[:, :, 0:resized_w] = resized_image
        return padding_im

    def __call__(self, img_list):
        img_num = len(img_list)
        # Calculate aspect ratio and sort for batching efficiency
        width_list = []
        for img in img_list:
            width_list.append(img.shape[1] / float(img.shape[0]))
        indices = np.argsort(np.array(width_list))

        rec_res = [["", 0.0]] * img_num
        batch_num = self.rec_batch_num
        elapse = 0

        for beg_img_no in range(0, img_num, batch_num):
            end_img_no = min(img_num, beg_img_no + batch_num)
            norm_img_batch = []
            max_wh_ratio = 0

            # Calculate max width/height ratio for this batch
            for ino in range(beg_img_no, end_img_no):
                h, w = img_list[indices[ino]].shape[0:2]
                wh_ratio = w * 1.0 / h
                max_wh_ratio = max(max_wh_ratio, wh_ratio)

            # Normalize images in batch
            for ino in range(beg_img_no, end_img_no):
                norm_img = self.resize_norm_img(img_list[indices[ino]], max_wh_ratio)
                norm_img = norm_img[np.newaxis, :]
                norm_img_batch.append(norm_img)

            norm_img_batch = np.concatenate(norm_img_batch)

            starttime = time.time()

            # Forward pass
            inp = mx.array(norm_img_batch)
            # PPLCNetV3 backbone already handles the transpose from (B, C, H, W) to (B, H, W, C)
            backbone_out = self.backbone(inp)
            head_out = self.head(backbone_out)

            preds = np.array(head_out)
            rec_result = self.postprocess_op(preds)
            for rno in range(len(rec_result)):
                rec_res[indices[beg_img_no + rno]] = rec_result[rno]
            elapse += time.time() - starttime

        return rec_res, elapse


def test_recognizer(args):
    loaded = np.load(
        "/Users/alexchen/Desktop/LocalDev/nexaml-mlx/examples/paddle_ocr/modelfiles/rec_input.npz"
    )
    img_list = [loaded[f"arr_{i}"] for i in range(len(loaded.files))]
    recognizer = TextRecognizer(args)
    # recognizer.load_weights(
    #     "/Users/alexchen/Desktop/LocalDev/nexaml-mlx/examples/paddle_ocr/modelfiles/ch_ptocr_v4_rec_infer.safetensors"
    # )
    # recognizer.save_weights(
    #     "/Users/alexchen/Desktop/LocalDev/nexaml-mlx/examples/paddle_ocr/modelfiles/ch_ptocr_v4_rec_infer.safetensors"
    # )
    # recognizer.set_dtype(mx.float16)
    # recognizer.save_weights(
    #     "/Users/alexchen/Desktop/LocalDev/nexaml-mlx/examples/paddle_ocr/modelfiles/ch_ptocr_v4_rec_infer_f16.safetensors"
    # )
    recognizer.load_weights(
        "/Users/alexchen/Desktop/LocalDev/nexaml-mlx/examples/paddle_ocr/modelfiles/ch_ptocr_v4_rec_infer_f16.safetensors"
    )
    recognizer.eval()  # Important for BatchNorm behavior in MLX

    rec_res, elapse = recognizer(img_list)
    print(f"Recognition results: {rec_res}")
    print(f"Recognition time: {elapse:.3f}s")


class TextSystem:
    """OCR text detection and recognition system"""
    def __init__(self, args):
        self.det = TextDetector(args)
        self.rec = TextRecognizer(args)
        self.drop_score = args.drop_score

        # Load weights from safetensors
        self.det.load_weights(args.det_model_path)
        self.rec.load_weights(args.rec_model_path)

        self.det.eval()
        self.rec.eval()

    @staticmethod
    def _order_boxes(boxes: np.ndarray) -> List[np.ndarray]:
        """Order detected boxes by position (top to bottom, left to right)"""
        return sorted(boxes, key=lambda b: (b[0][1], b[0][0]))

    @staticmethod
    def _crop_rotated(img: np.ndarray, pts: np.ndarray) -> np.ndarray:
        """Crop rotated text region from image"""
        pts = pts.astype("float32")
        w = int(max(np.linalg.norm(pts[0] - pts[1]), np.linalg.norm(pts[2] - pts[3])))
        h = int(max(np.linalg.norm(pts[0] - pts[3]), np.linalg.norm(pts[1] - pts[2])))
        M = cv2.getPerspectiveTransform(
            pts, np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype="float32")
        )
        dst = cv2.warpPerspective(img, M, (w, h), borderMode=cv2.BORDER_REPLICATE)
        if h / max(w, 1) > 1.5:
            dst = np.rot90(dst)
        return dst

    def __call__(self, img: np.ndarray) -> Tuple[List[np.ndarray], List[Tuple[str, float]]]:
        """Perform OCR on input image"""
        boxes = self.det(img)
        if boxes is None or len(boxes) == 0:
            return [], []

        boxes = self._order_boxes(boxes)
        crops = [self._crop_rotated(img, b.copy()) for b in boxes]

        rec_res, _ = self.rec(crops)

        keep_boxes, keep_txt = [], []
        for box, (txt, score) in zip(boxes, rec_res):
            if score >= self.drop_score:
                keep_boxes.append(box)
                keep_txt.append((txt, float(score)))
        return keep_boxes, keep_txt


if __name__ == "__main__":
    config = Config()
    text_system = TextSystem(config)
    # Test with a sample image from model directory if available
    img_path = os.path.join(config.model_cache_dir, "1.jpg")
    if not os.path.exists(img_path):
        print("No test image found. Please provide an image path for testing.")
        sys.exit(1)
    
    img = cv2.imread(img_path)
    if img is None:
        print(f"Error: Could not read image at {img_path}")
        sys.exit(1)

    boxes, txts = text_system(img)
    print(f"Detected {len(boxes)} boxes")
    print(f"Recognized text: {txts}")
