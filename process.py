import os
import nc
import json
from PIL import Image
from datetime import timedelta, datetime
from tqdm import tqdm


def gen_vis(df, cfg):
    """Displays a NetCDF visualization

    Arguments:
        df {DataFrame} -- Pandas DataFrame generated from NetCDF Dataset
    """

    plt_data = nc.gen_map(df, cfg)
    plt_data[0].show()


def export_img(cfg, plt, cmap, working_root, out_root, crop=True, dpi=300):
    """Exports a NetCDF visualization as PNG File

    Arguments:
        df {DataFrame} -- Pandas DataFrame from NetCDF Dataset

    Keyword Arguments:
        crop {bool} -- Determines if extraneous image info are cropped
                    (default: {True})
    """

    # Generating map from DataFrame
    # cmap = nc.gen_map(df, cfg)

    # Set export and temp directories
    working = f"{working_root}/{cfg['date']}_{dpi}.png"
    out = f"{out_root}/{cfg['date']}_{dpi}_{cmap}.png"  # noqa: E501 f"out/img/{cfg['date']}_{dpi}.png"

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
        # os.remove(working)  # Deletes temp map
    else:
        plt.savefig(out, dpi=dpi)
    return out


def __oisst_export__(y, m, d, do_csv=False, do_img=True, do_vis=False, temp_path="/", csv_path="/", stats_path="/", img_path="/"):  # noqa: E501
    mfill = str(m).zfill(2)
    dfill = str(d).zfill(2)

    tqdm.write("\nDownloading...")
    url = f"https://www.ncei.noaa.gov/data/sea-surface-temperature-optimum-interpolation/v2.1/access/avhrr/{y}{mfill}/oisst-avhrr-v02r01.{y}{mfill}{dfill}.nc"  # noqa: E501
    df, cfg = nc.process_url(url)
    tqdm.write("Downloaded & Processed!")

    # Show statistics
    stats = {}
    tqdm.write("\nStatistics:")
    column = df['sst']

    max = '%.2f' % round(column.max(), 2)
    stats['max'] = max
    tqdm.write(f"Max: {stats['max']}")

    min = '%.2f' % round(column.min(), 2)
    stats['min'] = min
    tqdm.write(f"Min: {stats['min']}")

    avg = '%.2f' % round(column.mean(), 2)
    stats['avg'] = avg
    tqdm.write(f"Avg: {stats['avg']}")

    std = '%.2f' % round(column.std(), 2)
    stats['std'] = std
    tqdm.write(f"StD: {stats['std']}")

    # Write local statistics to file
    with open(f"{stats_path}/{y}/{y}-{mfill}-{dfill}.json", 'w') as f:
        json.dump(stats, f, indent=4)

    # Write global statistics to file
    with open(f"{stats_path}/stats.json", 'r+') as f:
        obj = json.load(f)
        if float(stats['max']) < float(obj['max']):
            stats['max'] = obj['max']
        if float(stats['min']) > float(obj['min']):
            stats['min'] = obj['min']
        f.seek(0)
        json.dump(stats, f, indent=4)
        f.truncate()

    if do_csv:
        tqdm.write("\nExporting CSV...")
        df.to_csv(f"{csv_path}/{cfg['date']}_oisst.csv", index=False)
        tqdm.write("Exported!")

    if do_img:
        tqdm.write("\nGenerating image...")
        plt_data = nc.gen_plt(df, cfg)
        tqdm.write("Generated! Exporting image...")
        path = export_img(cfg, plt_data[0], plt_data[1], dpi=300, working_root=temp_path, out_root=img_path)  # noqa: E501
        tqdm.write("Exported!")

    return path


def __get_range__(start_date, end_date):
    """Returns list of timetuples in range [start_date,end_date]

    Arguments:
        start_date {str} -- Date for start of range "YYYY/MM/DD"
        end_date {str} -- Date for end of range "YYYY/MM/DD"

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


def oisst_day(date_string, do_csv=True, do_img=True, temp="", csv="", img="", stats="", _callback=None):  # noqa: E501
    day = datetime.strptime(date_string, '%Y/%m/%d').timetuple()
    __oisst_export__(day[0], day[1], day[2], do_csv, do_img, temp_path=temp, csv_path=csv, stats_path=stats, img_path=img)  # noqa: E501


def oisst_range(start_date, end_date, do_csv=True, do_img=True, temp="", csv="", img="", stats="", _callback=None):  # noqa: E501
    date_range = __get_range__(start_date, end_date)
    for day in tqdm(date_range):
        tqdm.write("\n----------------------------------------")
        tqdm.write(f"Processing data for {day[1]}/{day[2]}/{day[0]}")  # noqa: E501
        path = __oisst_export__(day[0], day[1], day[2], do_csv, do_img, temp_path=temp, csv_path=csv, stats_path=stats, img_path=img)  # noqa: E501
        if _callback:
            _callback(path, tqdm)
