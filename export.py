import process
import time
import os
import tqdm
import sys
from image_handler import modify_image
from datetime import timedelta, datetime


def export_day(date, year):
    process.oisst_day(date,  temp="temp/",
                        csv=f"out/data/{year}", img=f"out/img/{year}",
                        stats="out/stats/",
                        _callback=modify_image)


date_str = sys.argv[1]
year = date_str.split('/')[0]
date = datetime.strptime(date_str, '%Y/%m/%d').timetuple()

if not os.path.exists(f"out/data/{year}"):
        os.makedirs(f"out/data/{year}")

if not os.path.exists(f"out/img/{year}"):
    os.makedirs(f"out/img/{year}")

if not os.path.exists(f"out/stats/{year}"):
    os.makedirs(f"out/stats/{year}")

export_day(date, year)
