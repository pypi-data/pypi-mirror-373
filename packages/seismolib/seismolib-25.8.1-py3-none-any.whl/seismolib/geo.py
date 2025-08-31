import numpy as np

def epdist(event_lon, event_lat, station_lon, station_lat, is_elliptic=False):

    """
    2組の緯度経度から震央距離・Azimuth・Back Azimuthの計算を行う

    定式化は地震の辞典第2版 p.52に基づく．方位角は北から時計回りに測る．
    基本的には球面三角法だが，距離が近いときにベッセル楕円体の地心半径を
    用いた高精度計算（is_elliptic = True ) も行える．

    Parameters
    ----------
    event_lon, event_lat : float
        震源の緯度経度 (degrees)
    station_lon, station_lat : float
        観測点緯度経度（degrees）
                
    Return
    ------
    tuple
        (dist (km), azimuth (degree), back_azimuth (degree))
        
    Examples
    --------
    >>> epdist(135, 35, 136, 36)
    (143.38265213187395, 38.860270806043971, 219.4410056442396)

    >>> epdist(135, 35, 136, 36, True)
    (143.30662405398323, 38.986394043530979, 219.5645515565227)
    """

    R_EARTH = 6371.0   # 平均地球半径(km)
    e2 = 0.0066743722  # 地球楕円体の一次離心率の2乗（ベッセル楕円体定義）

    fe = np.deg2rad(event_lat)
    le = np.deg2rad(event_lon)
    fs = np.deg2rad(station_lat)
    ls = np.deg2rad(station_lon)

    # latitude should be 0 to 2*pi
    if le < 0:
        le = le + 2 * np.pi
    if ls < 0:
        ls = ls + 2 * np.pi

    # Convert geographical to gencentric latitude
    if is_elliptic:

        fe = np.arctan((1-e2) * np.tan(fe))
        fs = np.arctan((1-e2) * np.tan(fs))

    # 一般の場合の震央角距離
    a_e = np.cos(fe) * np.cos(le)
    a_s = np.cos(fs) * np.cos(ls)
    b_e = np.cos(fe) * np.sin(le)
    b_s = np.cos(fs) * np.sin(ls)
    c_e = np.sin(fe)
    c_s = np.sin(fs)

    dist = np.arccos(min(max(a_e*a_s + b_e*b_s + c_e*c_s, -1), 1))

    # Different, but mathematically equivalent representation of distance
    # for avoiding digit cancellation for short distance
    if np.rad2deg(dist) < 30:
        wk = (a_e-a_s)*(a_e-a_s) + (b_e-b_s)*(b_e-b_s) + (c_e-c_s)*(c_e-c_s)
        dist = 2.0 * np.arcsin(np.sqrt(wk) / 2)

    # Do not calculate distance if distance is too short
    if dist < 1e-15:
        az, baz = 0., 0.
    else:
        wk1 = min(max(
              (np.sin(fs)*np.cos(fe) -
               np.cos(fs)*np.sin(fe)*np.cos(ls-le)) / np.sin(dist), -1), 1)
        az = np.arccos(wk1)

        wk2 = min(max(
              (np.sin(fe)*np.cos(fs) -
               np.cos(fe)*np.sin(fs)*np.cos(le-ls)) / np.sin(dist), -1), 1)

        baz = np.arccos(wk2)

    dist *= R_EARTH          # km
    az  = np.rad2deg(az)     # deg
    baz = np.rad2deg(baz)    # deg

    # Correction by Bessel's ellipse for short distance
    MINIMUM_ANGLE_DIST = 30
    if is_elliptic and dist / np.rad2deg(R_EARTH) < MINIMUM_ANGLE_DIST:
        aa = 6377.397155  # Bessel's ellipse
        fa = (fs + fe) / 2.
        r_eb = aa*(1.0 - e2*np.sin(fa)**2 / 2 + e2*e2*np.sin(fa)**2 / 2 - (5./8.)*e2*e2*np.sin(fa)**4)
        dist = dist * r_eb / R_EARTH

    # Convert angles clockwise from north (0-360 deg.)
    if np.fabs(ls-le) <= 180.0:
        if le <= ls:                       # Station at eastward
            az = az
            baz = 360.0 - baz
        else:                              # Station at westward
            az = 360.0 - az
            baz = baz
    else:
        if le <= ls:                       # Station at westward
            az = 360.0 - az
            baz = baz
        else:                              # Station at eastward
            az = az
            baz = 360.0 - baz

    return (dist, az, baz)


def polygon(x, y, px, py):

    """
    Return if (x,y) is inside a polygon having vertices at (px(:), py(:))

    
    Parameters
    ----------
    x, y : float
        Location to be investigated
    px, py : Array-like
        Polygon vertices


    Returns
    -------
    bool
        True if (x,y) is inside the polygon


    Examples
    --------
    >>> polygon(0.5, 0.5, [0, 1, 1, 0], [0, 0, 1, 1])
    True

    >>> polygon(1.5, 1.5, [0, 1, 1, 0], [0, 0, 1, 1])
    False
    """

    n = len(px)

    # relative location vector
    vx = []
    vy = []
    for i in range(0, n):
        vx.append(px[i] - x)
        vy.append(py[i] - y)

    # vector length
    vlen = []
    for i in range(0, n):
        vlen.append(np.sqrt(vx[i]**2 + vy[i]**2))

    # True if the location (x, y) is equal to the vertex
    length_threshold = 1e-6
    for i in range(0, n):
        if vlen[i] < length_threshold:
            return True

    # check if the inside by summation of angle
    sumtheta = 0
    angle_threshold = 1e-6

    # Make the vector cyclic
    vx.append(vx[0])
    vy.append(vy[0])
    vlen.append(vlen[0])

    for i in range(0, n):
        # cos_theta estimation by cosine theorem
        wk = (vx[i] * vx[i+1] + vy[i] * vy[i+1]) / (vlen[i] * vlen[i+1])
        # avoid numerical error
        wk = min(max(wk, -1.0), 1.0)
        theta = np.arccos(wk)

        # True if the (x,y) is on the polygon's boundary
        if np.fabs(np.pi - np.fabs(theta)) < angle_threshold:
            return True
        sumtheta = sumtheta \
            + np.sign(vx[i] * vy[i+1] - vy[i] * vx[i+1]) * theta

    sumtheta = np.degrees(sumtheta)

    if -1 < np.fabs(sumtheta) - 360 < 1:
        return True
    else:
        return False


def deg2km(deg, R0=6371.0): 

    """ 角距離(deg.)を距離(km)に変換する．オプションで地球サイズ`R0`も変更できる．
    
    Parameters
    ----------
    deg : number
        角距離
    R0 : number, optional
        地球半径(6371kmがデフォルト）
    """

    return R0 * np.deg2rad(deg)


def km2deg(km, R0=6371.0): 

    """ 距離(km)を角距離(deg.)に変換する．オプションで地球サイズ`R0`も変更できる．
    
    Parameters
    ----------
    km : number
        距離
    R0 : number, optional
        地球半径(6371kmがデフォルト）
    """

    return np.rad2deg(km / R0)


def mercator_aspect(region, e=0.081819191042815790):

    """
    PyGMT形式で与えられた地図領域 [lon0, lon1, lat0, lat1] から，
    メルカトル投影された地図の縦横比Rを返す．
    ただし離心率 `e` のデフォルト値は地球のものが仮定されている．
    他惑星で利用するときはこの値をオプション変数として変更すること．
    """

    lambda_1 = np.deg2rad(region[0])
    lambda_2 = np.deg2rad(region[1])
    phi_1 = np.deg2rad(region[2])
    phi_2 = np.deg2rad(region[3])
    
    x1 = lambda_1
    x2 = lambda_2
    y1 = np.arctanh(np.sin(phi_1)) - e * np.arctanh(e*np.sin(phi_1))
    y2 = np.arctanh(np.sin(phi_2)) - e * np.arctanh(e*np.sin(phi_2))

    R = (y2 - y1) / (x2 - x1)

    return R

