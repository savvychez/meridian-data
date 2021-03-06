import process
import time
import os


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

    # im = cv2.imread(path)
    # mask = cv2.imread("in/mask.png")

    # diff_im = im - mask

    # cv2.imwrite(path, diff_im)


    # imgnp = np.array(img)
    # masknp = np.array(mask)

    # black = np.sum(masknp[:, :, :3], axis=2)
    # black_mask = np.any(black >= 0*3 or black <= 10*3, 1, 0)


    # alpha = np.where(black_mask, 0, imgnp[:, :, -1])

    # imgnp[:, :, -1] = alpha
    # return Image.fromarray(np.uint8(imgnp))


def modify_image(path, tqdm):
    tqdm.write("\nLoading image for Meridian3D view...")

    img = Image.open(path)
    img = img.convert("RGBA")

    tqdm.write("Loaded image! Converting alpha channel...")

    img = blackToAlpha(img)

    tqdm.write("Converted alpha channel! Adjusting for Equirectangular...")

    img = img.resize((5400, 2700))

    img = clearMask(img)

    tqdm.write("Resized! Exporting...")

    img.save(path, "PNG")

    tqdm.write("Export complete...\n")

def export_day(date, year, tqdm):
    process.oisst_day(date, tqdm,  temp="temp/",
                        csv=f"out/data/{year}", img=f"out/img/{year}",
                        stats="out/stats/",
                        _callback=modify_image)

# def export_days(start, end, year):
#     process.oisst_range(start, end, temp="temp/",
#                         csv=f"out/data/{year}", img=f"out/img/{year}",
#                         stats="out/stats/",
#                         _callback=modify_image)

def main():
    start = time.perf_counter()

    year = 2019

    if not os.path.exists(f"out/data/{year}"):
        os.makedirs(f"out/data/{year}")

    if not os.path.exists(f"out/img/{year}"):
        os.makedirs(f"out/img/{year}")

    if not os.path.exists(f"out/stats/{year}"):
        os.makedirs(f"out/stats/{year}")

