import datetime


def date_to_epoch_day(date: datetime.date) -> int:
    return (date - datetime.date(1970, 1, 1)).days if date else None


def datetime_to_time_stamp_millis(date_time: datetime.datetime) -> int:
    return int(date_time.timestamp() * 1000) if date_time else None
