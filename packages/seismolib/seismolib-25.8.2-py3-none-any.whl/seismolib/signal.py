import numpy as np
import scipy.fft as sf
import scipy.signal as ss


def time2freq(u, dt, nfft=None, sign="positive"):
    
    """
    Fourier transform of time series (real-valued) u(t) with sampling interval dt

    計算の定義は
    $$
        u(f) = sum_{i=0}^{N-1} u(t_i) exp[j 2 pi f t_i] dt
    $$
    ただし，オプション変数 sign='negative' のときには指数部の符号がマイナスになる．

    Parameters
    ----------
    u : array-like
        time series data (real)
    dt : float
        sampling interval (usualy in seconds)
    nfft : integer (optional)
        size of fft. Power of 2 is highly recommended for efficient computation
        default: len(u)
    sign : str
        'positive' or 'negative

    Returns
    -------
    c : array-like (Complex)
        Fourier transform of u
    f : array-like (size: nfft/2+1)
        Frequency (1/(unit of dt))
    """
    
    if nfft is None:
        nfft = len(u)

    if sign == "positive" or sign == "Positive":
        c = np.conjugate(sf.rfft(u, nfft))
    elif sign == "negative" or sign == "Negative":
        c = sf.rfft(u, nfft)

    f = sf.rfftfreq(nfft, dt)

    return c * dt, f


def freq2time(c, dt, nfft=None, sign="negative"):

    """
    Inverse of time2freq
        
    計算の定義は

    $$
        u(t) = sum_{i=0}^{N-1} u(f_i) exp[-j 2 pi f_i t] dt
    $$

    Parameters
    ----------
    c : array-like, complex
        fourier spectrum of u
    dt : float
        sampling interval (usualy in seconds)
    nfft : integer (optional)
        size of fft. Power of 2 is highly recommended for efficient computation
        default: (len(u)-1)*2
    sign : str
        'positive' or 'negative

    Returns
    -------
    u : array-like, real
        time series
    t : array-like, real
        time, starting from zero
    """

    if nfft is None:
        nfft = (len(c) - 1) * 2

    if sign == "negative" or sign == "Negative":
        u = sf.irfft(np.conjugate(c), nfft)
    elif sign == "positive" or sign == "Positive":
        u = sf.irfft(c, nfft)

    t = np.arange(0, nfft * dt, dt)

    return u / dt, t


def smooth(x, hw):

    """リスト x の半値幅 hw の移動平均を計算する．

    Arguments
    ---------
    x : array-like
        input data
    hw : integer
        half-window

    Returns
    -------
    y : array
        smoothed array of x
    """

    o = np.ones(2 * hw + 1) / (2 * hw + 1)
    y = np.convolve(x, o, "same")

    return y


def bp(dat, sfreq, fl, fh, nord, twopass):

    """band-pass filter

    Apply band-pass filter of nord-th order,
    with the corner frequencies of (fl, fh).
    Essentially same with obspy.signal.filter.bandpass

    Parameters
    ----------
    dat: numpy.ndarray
        Original data to be filtered
    sfreq: float/int
        Sampling frequency of data (usually in Hz)
    fl: float
        lower corner frequency of the band pass (the same unit w/sfreq)
    fh: float
        lower corner frequency of the band pass (the same unit w/sfreq)
    nord: int
        filter order
    twopass: bool
        apply the same filter from positive and netgative directions
        to realize zero-phase filter.
        In this case, filter order will be doubled.

    Returns
    -------
    numpy.ndarray
        Filtered data
    """

    fnyq = 0.5 * sfreq  # Nyquist frequency

    assert fl <= fh
    assert fh <= fnyq

    sos = ss.iirfilter(
        nord,
        (fl, fh),
        btype="bandpass",
        analog=False,
        ftype="butter",
        output="sos",
        fs=sfreq,
    )

    fdat = ss.sosfilt(sos, dat)

    if twopass:
        fdat = ss.sosfilt(sos, fdat[::-1])[::-1]

    return fdat


def lp(dat, sfreq, fh, nord, twopass):

    """low-pass filter

    Apply low-pass filter of nord-th order,
    with the corner frequencies of fh.
    Essentially same with obspy.signal.filter.bandpass

    Parameters
    ----------
    dat: numpy.ndarray)
        Original data to be filtered
    sfreq: float/int
        Sampling frequency of data (usually in Hz)
    fh: float
        Corner frequency of the low-pass filter (the same unit w/sfreq)
    nord: int
        filter order
    twopass: bool
        apply the same filter from positive and netgative directions
        to realize zero-phase filter.
        In this case, filter order will be doubled.

    Returns
    -------
    numpy.ndarray
        Filtered data
    """

    fnyq = 0.5 * sfreq  # Nyquist frequency

    assert fh <= fnyq

    sos = ss.iirfilter(
        nord, fh, btype="lowpass", analog=False, ftype="butter", output="sos", fs=sfreq
    )

    fdat = ss.sosfilt(sos, dat)

    if twopass:
        fdat = ss.sosfilt(sos, fdat[::-1])[::-1]

    return fdat


def hp(dat, sfreq, fl, nord, twopass):

    """high-pass filter

    Apply low-pass filter of nord-th order,
    with the corner frequencies of fh.
    Essentially same with obspy.signal.filter.bandpass

    Parameters
    ----------
    dat: numpy.ndarray)
        Original data to be filtered
    sfreq: float/int
        Sampling frequency of data (usually in Hz)
    fl: float
        corner frequency of the high-pass filter (the same unit w/sfreq)
    nord: int
        filter order
    twopass: bool
        apply the same filter from positive and netgative directions
        to realize zero-phase filter.
        In this case, filter order will be doubled.

    Returns
    -------
    numpy.ndarray
        Filtered data
    """

    fnyq = 0.5 * sfreq  # Nyquist frequency

    assert fl <= fnyq

    sos = ss.iirfilter(
        nord, fl, btype="highpass", analog=False, ftype="butter", output="sos", fs=sfreq
    )

    fdat = ss.sosfilt(sos, dat)

    if twopass:
        fdat = ss.sosfilt(sos, fdat[::-1])[::-1]

    return fdat


def taper_hamming(d):

    """Apply Hamming taper to data d

    Parameters
    ----------
    d : array-like
        input data

    Returns
    -------
    dt : array-like
         data with taper applied
    ta : array-like
         taper window array (`dt = d * ta`)
    """

    n = len(d)
    taper = ss.hamming(n)

    return d * taper, taper


def taper_hanning(d):

    """Apply Hanning (Han) taper to data d

    Parameters
    ----------
    d : array-like
        input data

    Returns
    -------
    dt : array-like
         data with taper applied
    ta : array-like
         taper window array (`dt = d * ta`)
    """
    n = len(d)
    taper = ss.hann(n)

    return d * taper, taper


def taper_cosine(d, r=5, nh=None):

    """Apply cosine (Tukey) taper to data d

    Parameters
    ----------
    d : array-like
        input data
    r:  float, optional (0-100)
        Fraction of the window inside the cosine taperd region in %
        0 is box-car window
        100 returns Hann window
    nh: integer
        instead of r, users may specify the length of taper region 
        by specifing number of samples in half-window nh

    Returns
    -------
    dt : array-like
         data with taper applied
    ta : array-like
         taper window array (`dt = d * ta`)
    """
    n = len(d)

    if nh is not None:
        r = 2*nh / n * 100
    
    taper = ss.windows.tukey(n, r / 100)

    return d * taper, taper


def rmean(u):

    """
    remove mean from array u
    
    Parameters
    ----------
    u : array-like
        input data
    
    Returns
    -------
    array-like
        data with mean subtracted
    """

    return u - np.mean(u)


def rtrend(u):

    """
    remove linear trend from array u
    This function is equivalent to scipy.signal.detrend
    
    Parameters
    ----------
    u : array-like
        input data
    
    Returns
    -------
    array-like
        detrended data
    """

    return ss.detrend(u)


def rtrend2(y):

    """
    Remove linear trend from array y
    The trend is estimated by least square method.

    Parameters
    ----------
    y : array-like
        input data
    
    Returns
    -------
    array-like
        detrended data
    """
    
    n = len(y)
    x = np.arange(n)    
    s_xx = x@x
    s_xy = x@y
    s_x = np.sum(x)
    s_y = np.sum(y)

    d = s_xx - s_x**2 / n
    a = (s_xy - s_x * s_y / n) / d
    b = (s_xx * s_y - s_xy * s_x) / n / d
    
    return y - (a * x + b)


def psdf_fft(u, dt, nfft=None, taper=None, alpha=0.2):

    """
    Power spectral density function by means of FFT

    Parameters
    ----------
    u : array-like
        time-series data of which PSDF is estimated.
    dt : float
        sampling interval (usually in sec.)
    nfft : int, optional
        number of samples to perform FFT. Power of 2 is highly recommended.
    taper : str, optional
        type of tapering window. 'Hanning'/'Hamming'/'Cosine'
        if taper is not None, Hamming is used as default taper window.
    alpha : float, optional
        Taper shape parameter for the 'Cosine' type taper.
        See `taper_cosine` for detail.
    """

    ndat = len(u)

    if nfft is None:
        nfft = len(u)

    u = rtrend(rmean(u))

    if taper == "Hamming":
        u, tap = taper_hamming(u)
    elif taper == "Hanning":
        u, tap = taper_hanning(u)
    elif taper == "Cosine":
        u, tap = taper_cosine(u, alpha)
    elif taper is not None:
        u, tap = taper_hamming(u)

    if taper is not None:
        taper_correction = tap @ tap / ndat
    else:
        taper_correction = 1

    c, freq = time2freq(u, dt, nfft)

    psdf = np.real(c * np.conj(c)) / (ndat * dt) / taper_correction

    psdf[1 : nfft // 2 - 1] *= 2  # double count for negative frequencies

    return psdf, freq


def envelope_hilbert(d):
    """
    ヒルベルト変換による時系列dのエンベロープ
    dの解析信号の絶対値として定義される．

    Parameters
    ---------
    d : array-like
        input data

    Returns
    -------
    array-like
        envelope of input data
    """

    return np.abs(ss.hilbert(d))


def envelope_rms(d, hw):
    """
    半値幅 hw のRMS平均による時系列 d のエンベロープ

    Parameters
    ---------
    d : array-like
        input data
    hw : half-window length

    Returns
    -------
    array-like
        envelope of input data
    """

    return np.sqrt(smooth(d * d, hw))


def rot_hcmp(data_x, data_y, cmpaz_x, cmpaz_y, rot_angle):

    """
    水平動2成分データを rot_angle 方向に回転する．

    角度はすべて北を0として時計回りに測る．入力地震動の成分は
    - x: 北から cmpaz_x 方向
    - y: 北から cmpaz_y 方向
    の成分を仮定する．わざわざ角度表現で2成分を独立にあらわしているのは，
    地震計の設置方位が南北東西から回転していることがあること，さらに
    cmpaz_y = cmpaz + 90
    であるとは限らないためである．たとえば東西成分の+-を逆につないだらcmpaz=-90である．
    NE→RT変換には rot_angle を back_azimuth - 180° とする

    Parameters
    ----------
    data_x, data_y: array-like
                    入力2成分データ．
                    標準的には南北と東西だがその方向はcmpaz_x, cmpaz_yで定義
    cmpaz_x, cmpaz_y: float or int
                      入力データの角度．北から時計回り．
                      南北動なら0，東西動なら90が入る．
    rot_angle: float or int
               data_x, data_y をそれぞれ この角度だけ時計周りに回転する．

    Returns
    -------
    data_v, data_w: array-like
                    それぞれdata_x, data_yを回転したもの
    """

    q_x = np.deg2rad(cmpaz_x)
    q_y = np.deg2rad(cmpaz_y)
    phi = np.deg2rad(rot_angle)

    data_v = np.cos(q_x - phi) * data_x + np.cos(q_y - phi) * data_y
    data_w = np.sin(q_x - phi) * data_x + np.sin(q_y - phi) * data_y

    return data_v, data_w


def seismometer_decon(dat, dt, f0=1.0, h0=0.7, f1=1/120, h1=1/np.sqrt(2)):

    """
    Inverse filterにより地震計特性の逆畳み込みと，広帯域特性の畳み込みを同時に行う．

    Parameters
    ----------
    dat: array-like
        地震波形データ
    dt: float
        サンプリング間隔
    f0, h0: floats
        入力記録の地震計の自然周波数とダンピング係数．デフォルトはHi-netの値
    f1, h1: floats
        出力記録の地震計の自然周波数とダンピング係数．デフォルトは120s, critical damping
    
    Returns
    -------
    dat: array-like 
        畳み込み後のデータ．元データと同じ長さ．

    
    Notes
    -----
    Maeda, T., Obara, K., Furumura, T., & Saito, T. (2011). 
    Interference of long-period seismic wavefield observed by dense Hi-net array in Japan, 
    Journal of Geophysical Research: Solid Earth, 116, B10303, doi:10.1029/2011JB008464. 
    http://doi.org/10.1029/2011JB008464

    """

    tw0 = np.tan(np.pi * f0 * dt)
    tw1 = np.tan(np.pi * f1 * dt)

    a = np.array([
         1.0 + 2.0 * h0 * tw0 +     tw0 * tw0, 
        -2.0 +                  2 * tw0 * tw0,
         1.0 - 2.0 * h0 * tw0 +     tw0 * tw0
    ])

    b = np.array([
         1.0 + 2.0 * h1 * tw1 +     tw1 * tw1, 
        -2.0 +                  2 * tw1 * tw1,
         1.0 - 2.0 * h1 * tw1 +     tw1 * tw1       
    ])

    return ss.lfilter(a, b, dat)
