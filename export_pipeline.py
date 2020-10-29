import process
import time
import os

from PIL import Image
import numpy as np


def blackToAlpha(img):
    imgnp = np.array(img)

    black = np.sum(imgnp[:, :, :3], axis=2)
    black_mask = np.where(black == 0*3, 1, 0)

    alpha = np.where(black_mask, 0, imgnp[:, :, -1])

    imgnp[:, :, -1] = alpha
    return Image.fromarray(np.uint8(imgnp))


def modify_image(path, tqdm):
    tqdm.write("\nLoading image for Meridian3D view...")

    img = Image.open(path)
    img = img.convert("RGBA")

    tqdm.write("Loaded image! Converting alpha channel...")

    img = blackToAlpha(img)

    tqdm.write("Converted alpha channel! Resizing for Equirectangular...")

    img = img.resize((10800, 5400))

    tqdm.write("Resized! Exporting...")

    img.save(path, "PNG")

    tqdm.write("Export complete...\n")


def main():
    start = time.perf_counter()

    year = 2019

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
