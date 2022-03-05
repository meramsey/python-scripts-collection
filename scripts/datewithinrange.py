from datetime import datetime, time, timedelta


# https://stackoverflow.com/a/62526868/1621381

def is_date_within(begin_time, span_time, check_date=None):
    """
    Return True if given check_date is within the interval beginning
    at begin_time with a duration of span_time.

    Args:
       - begin_time: datetime.time object
       - span_time: datetime.timedelta object
       - check_date: datetime.datetime object.
           If None, default to current UTC date
    """
    check_date = check_date or datetime.utcnow()
    if check_date.time() >= begin_time:
        begin_date = check_date.combine(check_date.date(), begin_time)
    else:
        begin_date = check_date.combine(check_date.date() - timedelta(days=1),
                                        begin_time)
    return begin_date <= check_date <= begin_date + span_time


def get_datetime_object_from_string(str):
    return datetime.strptime(str, "%Y-%m-%d %H:%M:%S")


date = datetime.strptime('2021-08-23 18:14:05', '%Y-%m-%d %H:%M:%S')
amount = 0.5
period = 'hours'
past = datetime.now() - timedelta(hours=amount)


# print(past)

# if past > date:
#     print(f"This is older than {amount} {period}")

# https://www.programiz.com/python-programming/datetime/strftime

def check_date_past_interval(check_date, interval=None):
    """Return True if given check_date is past the interval from current time.

    :param check_date: Datetime string like '2021-08-23 18:14:05'
    :type check_date: str
    :param interval: Hours amount to check in past.
    :type interval: int
    :return: Returns True if date exceeds interval.
    :rtype: bool
    """
    if interval is None:
        interval = 1
    date = datetime.strptime(str(check_date), '%Y-%m-%d %H:%M:%S')
    past = datetime.now() - timedelta(hours=interval)
    # Change period to period timedelta range provided as needed.
    period = 'hours'
    if past > date:
        print(f"This is older than {interval} {period}")
        return True
    elif past > date:
        return False
    else:
        return False


print(check_date_past_interval('2021-08-23 18:14:05'))
print(check_date_past_interval('2021-08-23 18:09:05'))
# if is_date_within(start_date, timedelta(hours=1), past):
#     print(f"{start_date} falls within last hour")

# test_date = datetime(2020, 6, 22, 11, 31)
# assert (is_date_within(time(10, 30), timedelta(hours=4), test_date) == True)
# assert (is_date_within(time(10, 30), timedelta(hours=1), test_date) == False)
#
# # Span midnight
# assert (is_date_within(time(23, 30), timedelta(hours=13), test_date) == True)
# assert (is_date_within(time(23, 30), timedelta(hours=1), test_date) == False)
