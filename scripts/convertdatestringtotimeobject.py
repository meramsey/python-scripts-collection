from datetime import datetime


def get_datetime_object_from_string(str, datetime_format="%Y-%m-%d%H:%M:%S"):
    """
    Get datetime object from datetime string and format string.
    Args:
        str (): DateTime string : 2022-01-27T14:49:01.125Z
        datetime_format (): Format string to use: "%Y-%m-%dT%H:%M:%S.%f%z"

    Returns: datetime object

    """
    return datetime.strptime(str, datetime_format)


def date_is_same_as_todays_date(datetime_obj):
    is_today = False
    today = datetime.today()
    if today.strftime("%Y-%m-%d") == datetime_obj.strftime("%Y-%m-%d"):
        is_today = True
        print(f"{datetime_obj} is from today....")
    else:
        print(f"{datetime_obj} not from today....")

    return is_today


other_date_time = get_datetime_object_from_string('2022-01-27T14:49:01.125Z', "%Y-%m-%dT%H:%M:%S.%f%z")

print(date_is_same_as_todays_date(other_date_time))
