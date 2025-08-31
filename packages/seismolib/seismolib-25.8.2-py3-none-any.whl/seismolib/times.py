import datetime as dt
import numpy as np

def time_range(start, stop, step=dt.timedelta(days=1)):

    """
    datetime.date オブジェクトの start, stop の間を step 間隔で返すジェネレータ
    yieldされるのは常にdatetime


    Parameters
    ----------
    start : datetime.date or datetime.datetime
        start day
    stop : datetime.date or datetime.datetime
        end day
    step : datetime.timdedelta
        step between start and stop

    Yields
    ------
    datetime.datetime

    Examples
    --------
    >>> for tim in time_range(datetime.date(2020, 10, 5), datetime.date(2020, 10, 7)):
    ...     print(tim)
    2020-10-05 00:00:00
    2020-10-06 00:00:00
    2020-10-07 00:00:00

    File
    ----
    seismolabpy/times.py
    """

    # 日付データの場合には 00:00:00 を追加してdatetime型にする
    if type(start) == dt.date:
        start = dt.datetime.combine(start, dt.time(0, 0, 0))
        stop = dt.datetime.combine(stop, dt.time(0, 0, 0))

    current = start

    while current <= stop:
        yield current

        current += step


def date2jul(date):

    """
    Returns julian day (day of the year).

    Parameters
    -----------
    date : datetime.date or datetime.datetime
        A datetime object of which the julian day is calculated

    Return
    ------
    julday: integer
        Julian day of the year

    Examples
    --------
    >>> date2jul(datetime.date(2015, 12, 31))
    365
    """

    return int(dt.datetime.strftime(date, "%j"))


def jul2date(year, julday):

    """
    Calculate datetime from year and julian day

    Parameters
    ----------
    year, juday: integer

    Return
    ------
    datetime.datetime

    Examples
    --------
    >>> jul2date(2000, 366)
    datetime.datetime(2000, 12, 31, 0, 0, 0)
    """

    return dt.datetime(year, 1, 1) + dt.timedelta(julday - 1)


def is_leapyear(yr):

    """
    True if the input yr is a leap year

    Parameters
    ----------
    yr: int

    Returns
    -------
    bool

    """

    return yr % 4 == 0 and yr % 100 != 0 or yr % 400 == 0


def timegm(tim):

    """
    Returns seconds from 1970-01-01 00:00:00 (UTC)

    Parameters
    ----------
    tim: datetime.datetime
        time to be converted

    Returns:
    tim: float
        time in seconds
    """

    if type(tim) == dt.date:
        tim = dt.datetime.combine(tim, dt.time(0, 0, 0))

    return tim.timestamp()


def gmtime(t):

    """
    Inverse of timegm

    Parameters
    ----------
    t: float or int
        seconds from 1970-01-01 00:00:00 (UTC)

    Returns
    -------
    date: datetime.datetime
    """
    return dt.datetime.fromtimestamp(t)


def date_time(year, month, day, hour, minute, second):

    """
    日時情報からdatetime.datetimeオブジェクトを返す．secondが実数でもOK

    Parameters
    ----------
    year   : int or str
    month  : int or str
    day    : int or str
    hour   : int or str
    minute : int or str
    second : int or float or str
        秒数は実数でも可．整数部とマイクロ秒部に分割してdatetimeに入力する．

    Returns
    -------
    result: datetime.datetime object

    Examples
    -------
    >>> date_time(2021, 10, 1, 0, 0, 0.5)
    datetime.datetime(2021, 10, 1, 0, 0, 0, 500000)

    """

    # float() や int() を噛ますのは，
    # 入力が文字列であっても正常に動作させるため
    fsec = float(second)
    isec = int(fsec)
    microsec = int(round((fsec - isec) * 1000)) * 1000
    return dt.datetime(
        int(year), int(month), int(day), int(hour), int(minute), isec, microsec
    )


def date(year, month, day):

    """
    日付のみの情報からdatetime.dateオブジェクトを返す．
    
    Parameters
    ----------
    year   : int or str
    month  : int or str
    day    : int or str

    Returns
    -------
    result: datetime.date object
    """
    return date_time(year, month, day, 0, 0, 0)


def to_datetime(datetime64):

    """
    convert numpy.datetime64 to datetime.datetime

    Parameters
    ----------
    datetime64: numpy.datetime64

    Returns
    -------
    datetime.datetime

    Note
    ----
    https://gist.github.com/blaylockbk/1677b446bc741ee2db3e943ab7e4cabd
    """

    ts = (datetime64 - np.datetime64("1970-01-01T00:00:00")) / np.timedelta64(1, "s")
    return dt.datetime.utcfromtimestamp(ts)
