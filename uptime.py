import psutil
from datetime import datetime

def get_time_difference(datetime1, datetime2, interval="default"):
    """
    Calculates the time difference between two datetime objects and returns it in a specified format.

    Args:
        datetime1 (datetime): The first datetime object.
        datetime2 (datetime): The second datetime object.
        interval (str, optional): The desired format of the time difference.
            Valid options are 'years', 'days', 'hours', 'minutes', 'seconds', or 'default'.
            Defaults to 'default', which returns a string with years, days, hours, minutes, and seconds.

    Returns:
        str or int: The time difference in the specified format.
            Returns an integer for 'years', 'days', 'hours', 'minutes', and 'seconds'.
            Returns a formatted string for 'default'.
    """

    duration = datetime2 - datetime1
    duration_in_seconds = duration.total_seconds()


    def calculate_years():
        return divmod(duration_in_seconds, 31536000)  # Seconds in a year

    def calculate_days(seconds=None):
        return divmod(seconds if seconds is not None else duration_in_seconds, 86400)  # Seconds in a day

    def calculate_hours(seconds=None):
        return divmod(seconds if seconds is not None else duration_in_seconds, 3600)  # Seconds in an hour

    def calculate_minutes(seconds=None):
        return divmod(seconds if seconds is not None else duration_in_seconds, 60)  # Seconds in a minute

    def calculate_seconds(seconds=None):
        if seconds is not None:
            return divmod(seconds, 1)
        return duration_in_seconds

    def get_total_duration():
        years = calculate_years()
        days = calculate_days(years[1])  # Use remainder to calculate next variable
        hours = calculate_hours(days[1])
        minutes = calculate_minutes(hours[1])
        seconds = calculate_seconds(minutes[1])
        ret = ""
        if years[0]>0:
            ret = ret + f"{int(years[0])} years "
        if days[0]>0:
            ret = ret + f"{int(days[0])} days "
        if hours[0]>0:
            ret = ret + f"{int(hours[0])} hours "
        if minutes[0]>0:
            ret = ret +f"{int(minutes[0]):d} minutes "
        if seconds[0]>0:
            ret = ret + f"{int(seconds[0])} seconds"
        return ret

    return {
        'years': int(calculate_years()[0]),
        'days': int(calculate_days()[0]),
        'hours': int(calculate_hours()[0]),
        'minutes': int(calculate_minutes()[0]),
        'seconds': calculate_seconds(),
        'default': get_total_duration()
    }[interval]


def bt_time():
    return datetime.fromtimestamp(psutil.boot_time())

def val():
    now = datetime.now()
    return get_time_difference(bt_time(), now)


def show():
    print(f"{bt_time().strftime("%Y-%m-%d %H:%M:%S")} up {val()}")

if __name__ == '__main__':
    show()