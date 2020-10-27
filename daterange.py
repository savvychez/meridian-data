from datetime import timedelta, datetime


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
