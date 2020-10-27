import os
import time
import json
import urllib
import xarray as xr
import seaborn as sb
import matplotlib.pyplot as plt
from PIL import Image
from tqdm import tqdm
from datetime import timedelta, datetime


def trim_nc(nc, cfg):
    """Drops unnecessary variables in XArray NetCDF data
    Arguments:
        nc {XArray Dataset} -- NetCDF4 Data loaded into XArray

    Keyword Arguments:
        typ {String} -- Info stored in NetCDF Dataset
    """

    for v in cfg['vars']:
        nc = nc.drop(v)
    nc = nc.squeeze()  # Clear row headers
    return nc


def parse_date(date):
    if "T" in date:
        return date.split("T")[0]
    return date


def process_file(file, type="oisst"):
    nc = xr.open_dataset(file)

    with open('cfg.json') as f:
        cfg = json.load(f)[type]
        cfg['date'] = parse_date(getattr(nc, cfg['date']))

    nc = trim_nc(nc, cfg)

    df = getattr(nc, cfg['pivot']).to_dataframe()
    df.reset_index(inplace=True)

    return df, cfg


def process_url(url):
    file = urllib.request.urlretrieve(url)
    return process_file(file[0])


def gen_csv(df, cfg):
    df.to_csv(f"out/data/{cfg['date']}.csv", index=False)


def gen_map(df, cfg):
    """Generates heatmap from NetCDF Dataframe

    Arguments:
        df {Pandas Dataframe} -- Dataframe containing lat, lon, pivot variable
    """

    # Pivots Dataframe into 3 Dimensions
    df = df.pivot("lat", "lon", cfg['pivot'])

    # Mask NaN values (Land & Unknown Temps)
    MASK = df.isnull()

    # Render Data into heatmap
    cmap = "rainbow"
    MAP = sb.heatmap(df, mask=MASK, cmap=cmap, cbar=True, vmin=0)
    MAP.set_facecolor('xkcd:black')
    MAP.invert_yaxis()
    return cmap


def gen_vis(df, cfg):
    """Displays a NetCDF visualization

    Arguments:
        df {DataFrame} -- Pandas DataFrame generated from NetCDF Dataset
    """

    gen_map(df, cfg)
    plt.show()


def gen_img(df, cfg, crop=True, dpi=300):
    """Exports a NetCDF visualization as PNG File

    Arguments:
        df {DataFrame} -- Pandas DataFrame from NetCDF Dataset

    Keyword Arguments:
        crop {bool} -- Determines if extraneous image info are cropped
                    (default: {True})
    """

    # Generating map from DataFrame
    cmap = gen_map(df, cfg)

    # Set export and temp directories
    working = f"working/{cfg['date']}_{dpi}.png"
    out = f"C:/Users/savvy/Dropbox/WebDev/meridian/{cfg['date']}_{dpi}_{cmap}.png"  # noqa: E501 f"out/img/{cfg['date']}_{dpi}.png"

    if crop:
        # Pre-exports image to working directory
        plt.savefig(working, dpi=dpi)

        # Creates temporary colored and greyscale maps
        temp = Image.open(working)
        grey = temp.convert("L")

        # Gets Y value for start (Iterates downw until first white pixel)
        starty = 0
        while grey.getpixel((grey.width/2, starty)) == 255:
            starty += 1

        # Gets X value for start (Iterates right until first non-white pixel)
        startx = 0
        while grey.getpixel((startx, starty)) == 255:
            startx += 1

        # Gets X value for endpoint (Iterates left until at right corner)
        endx = temp.width-1
        while grey.getpixel((endx, starty)) == 255:
            endx -= 1
        endx += 1

        # Gets Y value for endpoint (Iterates down until first white pixel)
        endy = int(starty)
        while grey.getpixel((endx-1, endy)) != 255:
            endy += 1

        cropped = temp.crop((startx, starty, endx, endy))

        # Switches west & east to normalize map
        width = cropped.width
        half = int(width/2)
        b = cropped.crop((0, 0, half, cropped.height))
        a = cropped.crop((width-half, 0, width, cropped.height))
        cropped.paste(a, (0, 0))
        cropped.paste(b, (half, 0))

        # Exports cropped map
        cropped.save(out, quality=100)
        os.remove(working)  # Deletes temp map
    else:
        plt.savefig(out, dpi=dpi)


def oisst_export(y, m, d, doimg=True, docsv=True):
    mfill = str(m).zfill(2)
    dfill = str(d).zfill(2)

    tqdm.write("Downloading...")
    url = f"https://www.ncei.noaa.gov/data/sea-surface-temperature-optimum-interpolation/v2.1/access/avhrr/{y}{mfill}/oisst-avhrr-v02r01.{y}{mfill}{dfill}.nc"  # noqa: E501
    df, cfg = process_url(url)
    tqdm.write("Downloaded & Processed!")

    if docsv:
        tqdm.write("Exporting CSV...")
        gen_csv(df, cfg)
        tqdm.write("Exported!")

    if doimg:
        tqdm.write("Generating image...")
        gen_img(df, cfg, crop=False)
        tqdm.write("Generated!")


def get_range(start_date, end_date):
    """Returns list of timetuples in range [start_date,end_date]

    Arguments:
        start_date {str} -- Date for start of range ("YYYY/MM/DD")
        end_date {str} -- Date for end of range ("YYYY/MM/DD")

    Returns:
        list[timetuple] -- [0][0] -> year, [0][1] -> month, [0][2] -> day
    """

    start_date = datetime.strptime(start_date, '%Y/%m/%d')
    end_date = datetime.strptime(end_date, '%Y/%m/%d')

    day_count = (end_date - start_date).days + 1
    days = []
    for date in [d for d in (start_date + timedelta(n) for n in range(day_count)) if d <= end_date]:  # noqa: E501
        days.append(date.timetuple())
    return days


def main():
    st = time.perf_counter()
    drange = get_range("2020/04/01", "2020/04/02")
    for day in tqdm(drange):
        tqdm.write(f"\nExporting data for {day[1]}/{day[2]}/{day[0]}")  # noqa: E501
        oisst_export(day[0], day[1], day[2])
    ft = time.perf_counter()-st
    print(f"Script executed successfully in {ft:0.2f} seconds")


main()
# , position=0, leave=True
