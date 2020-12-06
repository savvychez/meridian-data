import process
import time
import os
import tqdm
import sys
from datetime import timedelta, datetime

from PIL import Image
import numpy as np
import cv2

def blackToAlpha(img):
    imgnp = np.array(img)

    black = np.sum(imgnp[:, :, :3], axis=2)
    black_mask = np.where(black == 0*3, 1, 0)

    alpha = np.where(black_mask, 0, imgnp[:, :, -1])

    imgnp[:, :, -1] = alpha
    return Image.fromarray(np.uint8(imgnp))


def clearMask(img):
    mask = Image.open("in/mask_5k.png")
    mask = mask.convert("RGBA")

    img.paste(mask, (0, 0), mask)

    imgnp = np.array(img)

    mask = (imgnp[:, :, 0] == imgnp[:, :, 1]) & (imgnp[:, :, 2] == imgnp[:, :, 1])
    black_mask = np.where(mask, 1, 0)

    alpha = np.where(black_mask, 0, imgnp[:, :, -1])

    imgnp[:, :, -1] = alpha
    return Image.fromarray(np.uint8(imgnp))


def modify_image(path):
    print("\nLoading image for Meridian3D view...")

    img = Image.open(path)
    img = img.convert("RGBA")

    print("Loaded image! Converting alpha channel...")

    img = blackToAlpha(img)

    print("Converted alpha channel! Adjusting for Equirectangular...")

    img = img.resize((5400, 2700))

    img = clearMask(img)

    print("Resized! Exporting...")

    img.save(path, "PNG")

    print("Export complete...\n")