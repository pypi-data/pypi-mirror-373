# time-related functions
# (I can never remember them, so I'll have my own.)

from datetime import datetime


def time_format(format, time):
    if time is None:
        time = datetime.now()
    return time.strftime(format)


def isotime(time=None):
    return time_format("%Y%m%d:%H%M%S", time)


def isotime_ms(time=None):
    return time_format("%Y%m%d:%H%M%S.%f", time)[:-3]


def iso_time(time=None, sep="T"):
    return time_format("%Y-%m-%d{}%H:%M:%S".format(sep), time)


def iso_time_us(time=None, sep="T"):
    return time_format("%Y-%m-%d{}%H:%M:%S.%f".format(sep), time)


def iso_time_ms(time=None, sep="T"):
    return time_format("%Y-%m-%d{}%H:%M:%S.%f".format(sep), time)[:-3]

