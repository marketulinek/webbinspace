import datetime as dt


def adjust_number_by_range(number, lowest_number, highest_number):
    if number > highest_number:
        return highest_number
    if number < lowest_number:
        return lowest_number
    return number


def get_observing_progress(start_time, duration):
    """Returns the integer representing
    the percentage of target's observing progress.

    Ensures that the returned value is between 0 and 100.
    """
    percentage = calculate_time_progress(start_time, duration)
    return adjust_number_by_range(percentage, 0, 100)


def calculate_time_progress(start_time, duration):
    """Calculates the progress over a period of time.

    Returns integer as percentage.
    """

    ts_start = int(round(start_time.timestamp()))
    ts_duration = int(round(duration.total_seconds()))
    ts_now = int(round(dt.datetime.now().timestamp()))

    return (ts_now - ts_start) * (100 / ts_duration)
