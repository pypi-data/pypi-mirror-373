import numpy as np

def dms2deg(d, m, s):

    """
    60進法の degree(d):minute(m):second を 10進法のdegreeに変換する

    Parameters
    ----------
    d : number
        degree. can be either positive or negative
    m : number
        minutes. usually positive
    s : number
        seconds. usually positive

    Returns
    -------
    deg : float
        degrees in decimal
    """

    dd = np.sign(d) * ( abs(float(d)) + float(m)/60.0 + float(s) / 3600.0 )

    return dd


def deg2dms(deg): 

    """
    10進法のdegree を60進法の degree(d):minute(m):second に変換する
    
    Paremters
    ---------
    deg : number
          degree in decimal

    Returns
    -------
    (d, m, s) : tuple of numbers
        where d, m, s means degree, minute, and second
        d and m should be integer, while s is float. 
    """

    dd = abs(deg)
    s = int(np.sign(deg))
    d = s * int(dd)
    m = int( (dd - abs(d)) * 60 )
    s = (dd - abs(d)) * 60 * 60 - m * 60

    return d, m, s


def i2s(i, w=-1):

    """
    integer to string

    整数値 i を桁数 w の文字列にする．桁数がwに満たない場合は左にゼロを埋める．
    桁数が指定されていない場合は必要な最小限の長さの文字列になる．
    桁数が指定され，かつ足りない場合はAssertionErrorになる．

    Parameters
    ----------
    i : int
        integer to be converted
    w : int
        column width

    Returns
    -------
    result: str
        string representing integer i

    Examples
    --------
    >>> i2s(3, 5)
    '00003'
    
    >>> i2s(-1, 3)
    '-01'

    >>> i2s(-32351)
    '-32351
    """

    if i == 0: 
        w_true = 1
    elif i > 0: 
        w_true = int(np.floor(np.log10(abs(i)))) + 1
    else: 
        w_true = int(np.floor(np.log10(abs(i)))) + 1 + 1

    if w <= 0: 
        w = w_true
    
    assert i == 0 or w_true <= w

    return str(i).zfill(w)


def chk_value(var, err):

    """
    伝統的なエラー判定「未定義の場合に -12345.0 を取る」のような条件を判断する．

    未定義定数 err に値が十分近い場合には Noneを，そうでない場合には varを返す．
    整数・実数・複素数・文字列に対応．

    Parameters
    ----------
    var : int or float or complex or str
        検査値
    err : int or float or complex or str
        エラー判定定数

    Returns
    -------
    result : same type with var
        var or None

    Examples
    --------
    >>> chk_value(3.0, 3.0)


    >>> chk_value(3.1, 3.0)
    3.1

    >>> chk_value('3.1', 'abc')
    '3.1'
    """

    if isinstance(var, (int, str)):

        if var != err:
            return var
        else:
            return None

    elif isinstance(var, (float, complex)):

        if not np.isclose(var, err):
            return var
        else:
            return None

    else:
        raise TypeError("input type " + str(type(var)) + " is not supported")


def split_list(l, n):
    """
    split list into lists whose length of n

    Examples
    --------
    
    >>> for li in split_list(glob.glob(*),10):
    >>>     for f in li:
    >>>         print(f)
    
    """
    for idx in range(0, len(l), n):
        yield l[idx:idx + n]