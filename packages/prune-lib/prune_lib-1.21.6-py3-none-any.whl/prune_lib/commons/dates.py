from datetime import datetime, timedelta


def add_months(dt: datetime, *, months: int) -> datetime:
    new_month = (dt.month - 1 + months) % 12 + 1
    new_month_plus_one = new_month % 12 + 1
    new_year = dt.year + (dt.month - 1 + months) // 12

    # Find the last day of the new month to avoid day overflow (e.g., from January 31 to February)
    day = min(
        dt.day, (datetime(new_year, new_month_plus_one, 1) - timedelta(days=1)).day
    )

    return dt.replace(year=new_year, month=new_month, day=day)


def get_datetime_of_first_day_of_month() -> datetime:
    now = datetime.now()
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
