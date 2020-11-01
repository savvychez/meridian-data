from export_pipeline import export_day
from datetime import timedelta, datetime
from tqdm import tqdm
import os

def __get_range__(start_date, end_date):
    """Returns list of timetuples in range [start_date,end_date]

    Arguments:
        start_date {str} -- Date for start of range "YYYY/MM/DD"
        end_date {str} -- Date for end of range "YYYY/MM/DD"

    Returns:
        list[timetuple] -- [0][0] -> year, [0][1] -> month, [0][2] -> day
    """

    start_date = datetime.strptime(str(start_date), '%Y/%m/%d')
    end_date = datetime.strptime(str(end_date), '%Y/%m/%d')

    day_count = (end_date - start_date).days + 1
    days = []
    for date in [d for d in (start_date + timedelta(n) for n in range(day_count)) if d <= end_date]:  # noqa: E501
        days.append(date.timetuple())
    return days


def main():
    start = str(input("Start Date YYYY/MM/DD: "))
    end = str(input("End Date YYYY/MM/DD: "))
    year = input("Year: ")

    date_range = __get_range__(start, end)

    if not os.path.exists(f"out/data/{year}"):
        os.makedirs(f"out/data/{year}")

    if not os.path.exists(f"out/img/{year}"):
        os.makedirs(f"out/img/{year}")

    if not os.path.exists(f"out/stats/{year}"):
        os.makedirs(f"out/stats/{year}")

    for day in tqdm(date_range):
        export_day(day, year, tqdm)

main()