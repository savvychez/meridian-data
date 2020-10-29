import json
import urllib
import xarray as xr
import seaborn as sb
import matplotlib.pyplot as plt


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

    with open('config.json') as f:
        cfg = json.load(f)[type]
        cfg['date'] = parse_date(getattr(nc, cfg['date']))

    nc = trim_nc(nc, cfg)

    df = getattr(nc, cfg['pivot']).to_dataframe()
    df.reset_index(inplace=True)

    return df, cfg


def process_url(url):
    file = urllib.request.urlretrieve(url)
    return process_file(file[0])


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
    MAP = sb.heatmap(df, mask=MASK, cmap=cmap, cbar=False, vmin=0)
    MAP.set_facecolor('xkcd:black')
    MAP.invert_yaxis()
    return "oisst"


def gen_plt(df, cfg):
    """Exports a NetCDF visualization as PNG File

    Arguments:
        df {DataFrame} -- Pandas DataFrame from NetCDF Dataset
        cfg {list} -- File configuration parameters

    Keyword Arguments:
        crop {bool} -- Determines if extraneous image info are cropped
                    (default: {True})
    """

    # Generating map from DataFrame
    cmap = gen_map(df, cfg)

    return [plt, cmap]
