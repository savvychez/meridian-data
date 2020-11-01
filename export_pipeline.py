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

    del img
    del black
    del black_mask
    del alpha 

    return Image.fromarray(np.uint8(imgnp))


def clearMask(img):
    mask = Image.open("in/mask.png")
    mask = mask.convert("RGBA")

    img.paste(mask, (0, 0), mask)

    imgnp = np.array(img)

    mask = (imgnp[:, :, 0] == imgnp[:, :, 1]) & (imgnp[:, :, 2] == imgnp[:, :, 1])
    black_mask = np.where(mask, 1, 0)

    alpha = np.where(black_mask, 0, imgnp[:, :, -1])

    imgnp[:, :, -1] = alpha

    del img
    del mask
    del black_mask
    del alpha

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

    img2 = blackToAlpha(img)
    del img 

    tqdm.write("Converted alpha channel! Adjusting for Equirectangular...")

    img3 = img2.resize((5400, 2700))

    del img2

    img4 = clearMask(img3)

    del img3

    tqdm.write("Resized! Exporting...")

    img4.save(path, "PNG")

    del img4

    tqdm.write("Export complete...\n")


def main():
    start = time.perf_counter()

    year = input("Year:")

    if not os.path.exists(f"out/data/{year}"):
        os.makedirs(f"out/data/{year}")

    if not os.path.exists(f"out/img/{year}"):
        os.makedirs(f"out/img/{year}")

    if not os.path.exists(f"out/stats/{year}"):
        os.makedirs(f"out/stats/{year}")

    process.oisst_range(f"{year}/01/01", f"{year}/01/05", temp="temp/",
                        csv=f"out/data/{year}", img=f"out/img/{year}",
                        stats="out/stats/",
                        _callback=modify_image)

    end = time.perf_counter()-start
    print(f"\nScript executed successfully in {end:0.2f} seconds")


main()
