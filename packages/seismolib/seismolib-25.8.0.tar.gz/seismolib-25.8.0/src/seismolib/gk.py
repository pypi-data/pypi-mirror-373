""" Gauss-Krugeur projection based on GSI's formula

    http://goo.gl/qoYh8t, http://goo.gl/mSuDxm
"""

import numpy as np

def ll2xy(lon, lat, clon, clat):

    """ Convert longitude & latitude (deg.) to x, y (km)
    
    Parameters
    ----------
    lon, lat: float
        longitude and latitude (degrees) to be converted to cartesian
    clon, clat: float
        longitude and latitude of reference point (deg.)

    Returns
    -------
    x, y : float
        Northing/Easting coordinate (km) measured from (clon, clat)

    Example
    -------
    >>> ll2xy(144, 43, 144.25, 44)
    (-111.061047360681, -20.38320805146281)
    """

    lam, phi = np.deg2rad(lon),  np.deg2rad(lat)
    lam0, phi0 = np.deg2rad(clon), np.deg2rad(clat)

    e2n = 2 * np.sqrt(_n) / (1 + _n)
    lam_c, lam_s = np.cos(lam - lam0), np.sin(lam - lam0)

    tan_chi = np.sinh(np.arctanh(np.sin(phi)) - e2n * np.arctanh(e2n * np.sin(phi)))
    cos_chi = np.sqrt(1 + tan_chi**2)

    xi = np.arctan(tan_chi / lam_c)
    eta = np.arctanh(lam_s / cos_chi)

    Ab = _m0 * _a / (1 + _n) * _A[0]

    x, y = xi, eta
    for i in range(0, 5):
        x += _alpha[i] * np.sin(2*(i+1)*xi) * np.cosh(2*(i+1)*eta)
        y += _alpha[i] * np.cos(2*(i+1)*xi) * np.sinh(2*(i+1)*eta)

    x = (Ab * x - _S_phi(phi0)) / 1000
    y = (Ab * y) / 1000

    return x, y


def xy2ll(x, y, clon, clat):

    """ Convert x & y (km) to x, y (km). Inverse of ll2xy

    Parameters
    ----------
    x, y : float
        Northing & easting coordinate location measured from reference (km)
    clon, clat : float
        longitude and latitude of reference point (degrees)

    Returns
    -------
    lon, lat: float
        longitude and latitude (degrees)

    Example
    -------
    >>> sl.xy2ll(-111.061047360681, -20.38320805146281, 144.25, 44)
    (144.0, 43.0)
    """

    lam0, phi0 = np.deg2rad(clon), np.deg2rad(clat)

    Ab = _m0 * _a / (1 + _n) * _A[0]
    xi = (x * 1000 + _S_phi(phi0)) / Ab
    eta = y * 1000. / Ab

    xi2, eta2 = xi, eta

    for i in range(0, 5):
        xi2 -= _beta[i] * np.sin(2*(i+1)*xi) * np.cosh(2*(i+1)*eta)
        eta2 -= _beta[i] * np.cos(2*(i+1)*xi) * np.sinh(2*(i+1)*eta)

    chi = np.arcsin(np.sin(xi2) / np.cosh(eta2))
    lam = lam0 + np.arctan(np.sinh(eta2) / np.cos(xi2))
    phi = chi

    for i in range(0, 6):
        phi += _delta[i] * np.sin(2*(i+1)*chi)

    lon = np.rad2deg(lam)
    lat = np.rad2deg(phi)

    return lon, lat

def _S_phi(phi0):

    """ Calculate Meridian convergence angle """

    sphi = _A[0] * phi0
    for i in range(1, 6):
        sphi += _A[i] * np.sin(2*i*phi0)

    sphi *= _m0 * _a / (1 + _n)

    return sphi

#
# constants used inside the module
#

_F = 298.257222101  # inverse elliplicity of the Earth
_n = 1 / (2 * _F - 1)
_a = 6378137.0     # earth radius
_m0 = 0.9999

_nn = np.array([1, _n, _n**2, _n**3, _n**4, _n**5, _n**6])

_acoef = np.array(
    [[1/2,  -2/3,    5/16,        41/180,     -127/288],
     [0,   13/48,    -3/5,      557/1440,      281/630],
     [0,       0,  61/240,      -103/140,  15061/26880],
     [0,       0,       0,  49561/161280,     -179/168],
     [0,       0,       0,             0,  34729/80640]])

_bcoef = np.array(
    [[1/2, -2/3,   37/96,       -1/360,      -81/512],
     [0,   1/48,    1/15,    -437/1440,       46/105],
     [0,      0,  17/480,      -37/840,    -209/4480],
     [0,      0,       0,  4397/161280,      -11/504],
     [0,      0,       0,            0,  4583/161280]])

_dcoef = np.array(
    [[2, -2/3,     -2,    116/45,     26/45,     -2854/675],
     [0,  7/3,   -8/5,   -227/45,  2704/315,      2323/945],
     [0,    0,  56/15,   -136/35, -1262/105,    73814/2835],
     [0,    0,      0,  4279/630,   -332/35, -399572/14175],
     [0,    0,      0,         0,  4174/315,  -144838/6237],
     [0,    0,      0,         0,         0,  601676/22275]])

_Acoef = np.array(
    [[1,     0,    1/4,       0,     1/64,          0],
     [0,  -3/2,      0,    3/16,        0,      3/128],
     [0,     0,  15/16,       0,   -15/64,          0],
     [0,     0,      0,  -35/48,        0,    175/768],
     [0,     0,      0,       0,  315/512,          0],
     [0,     0,      0,       0,        0,  -693/1280]])

_alpha = _acoef.dot(_nn[1:6])

_beta = _bcoef.dot(_nn[1:6])

_delta = _dcoef.dot(_nn[1:7])

_A = _Acoef.dot(_nn[0:6])

