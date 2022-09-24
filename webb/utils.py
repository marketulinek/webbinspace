import datetime as dt


def get_observing_progress(start_time, duration):
    """Returns the integer representing the percentage of target's observing progress.
    
    Ensures that the returned value is between 0 and 100.
    """
    percentage = calculate_time_progress(start_time, duration)

    if percentage > 100:
        return 100
    elif percentage < 0:
        return 0
    else:
        return percentage

def calculate_time_progress(start_time, duration):
    """Calculates the progress over a period of time.

    Returns integer as percentage.
    """

    ts_start = int(round(start_time.timestamp()))
    ts_duration = int(round(duration.total_seconds()))
    ts_now = int(round(dt.datetime.now().timestamp()))

    return (ts_now - ts_start) * (100 / ts_duration)