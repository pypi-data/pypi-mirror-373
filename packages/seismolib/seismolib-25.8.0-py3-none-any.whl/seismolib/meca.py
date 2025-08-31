"""mechanism"""
import numpy as np
from numpy import sin, cos, arcsin, arccos, arctan2, pi, rad2deg, deg2rad


def kagan_angle(strike1, dip1, rake1, strike2, dip2, rake2): 
    """Kagan's Angle"""
    
    # tension, prssure, & nul axises
    t1, p1, b1 = sdr2tpb(strike1, dip1, rake1)
    t2, p2, b2 = sdr2tpb(strike2, dip2, rake2)

    tt = np.dot(t1, t2)
    pp = np.dot(p1, p2)
    bb = np.dot(b1, b2)

    phi1 = arccos(( tt + pp + bb - 1) / 2)
    phi2 = arccos((-tt - pp + bb - 1) / 2)
    phi3 = arccos((-tt + pp - bb - 1) / 2)
    phi4 = arccos(( tt - pp - bb - 1) / 2)
    
    kangle = rad2deg(min(phi1, phi2, phi3, phi4))

    return kangle

def radipat(strike, dip, rake, azimuth, takeoff): 
    """ Radiation pattern of P, SV, and SH waves

    Reference: Aki & Richards (2002) p.108
    """

    fs = deg2rad(strike)
    d  = deg2rad(dip)
    l  = deg2rad(rake)
    f  = deg2rad(azimuth)
    ix = deg2rad(takeoff)

    FP   = cos(l) * sin(d)   * sin(ix)**2 * sin(2*(f-fs)) \
         - cos(l) * cos(d)   * sin(2*ix)  * cos(f-fs) \
         + sin(l) * sin(2*d) * ( cos(ix)**2 - sin(ix)**2 * sin(f-fs)**2 ) \
         + sin(l) * cos(2*d) * sin(2*ix) * sin(f-fs)

    FSV  = sin(l) * cos(2*d) * cos(2*ix) * sin(f-fs) \
         - cos(l) * cos(d)   * cos(2*ix) * cos(f-fs) \
         + cos(l) * sin(d)   * sin(2*ix) * sin(2*(f-fs)) / 2 \
         - sin(l) * sin(2*d) * sin(2*ix) * ( 1 + sin(f-fs)**2 )
    
    FSH  = cos(l) * cos(d)   * cos(ix) * sin(f-fs) \
         + cos(l) * sin(d)   * sin(ix) * cos(2*(f-fs)) \
         + sin(l) * cos(2*d) * cos(ix) * cos(f-fs) \
         - sin(l) * sin(2*d) * sin(ix) * sin(2*(f-fs))/2
    
    return FP, FSV, FSH


def sdr2moment(strike, dip, rake, M0): 
    """calculate moment tensor component from strike, dip, and rake
    """

    sinδ  = sin(    deg2rad(dip   ))
    cosδ  = cos(    deg2rad(dip   ))
    sin2δ = sin(2 * deg2rad(dip   ))
    cos2δ = cos(2 * deg2rad(dip   ))
    sinλ  = sin(    deg2rad(rake  ))
    cosλ  = cos(    deg2rad(rake  ))
    sinφ  = sin(    deg2rad(strike))
    cosφ  = cos(    deg2rad(strike))
    sin2φ = sin(2 * deg2rad(strike))
    cos2φ = cos(2 * deg2rad(strike))
    
    Mxx = - M0 * (sinδ * cosλ * sin2φ + sin2δ * sinλ * sinφ * sinφ )
    Mxy =   M0 * (sinδ * cosλ * cos2φ + sin2δ * sinλ * sin2φ / 2    )
    Mxz = - M0 * (cosδ * cosλ * cosφ  + cos2δ * sinλ * sinφ         )
    Myy =   M0 * (sinδ * cosλ * sin2φ - sin2δ * sinλ * cosφ * cosφ )
    Myz = - M0 * (cosδ * cosλ * sinφ  - cos2δ * sinλ * cosφ         )
    Mzz =   M0 * (                         sin2δ * sinλ                 )

    return Mxx, Myy, Mzz, Myz, Mxz, Mxy

def moment_xyz2rqf(Mxx, Myy, Mzz, Myz, Mxz, Mxy): 

    Mrr =   Mzz
    Mqq =   Mxx
    Mff =   Myy
    Mrq =   Mxz
    Mqf = - Mxy
    Mrf = - Myz

    return Mrr, Mqq, Mff, Mqf, Mrf, Mrq


def moment_rqf2xyz(Mrr, Mqq, Mff, Mqf, Mrf, Mrq): 

    Mxx =   Mqq
    Myy =   Mff
    Mzz =   Mrr
    Myz = - Mrf
    Mxz =   Mrq
    Mxy = - Mqf

    return Mxx, Myy, Mzz, Myz, Mxz, Mxy


def ns2sdr(n, s): 
    """normal and slip vector n&d to strike, dip, rake angles
    """

    dip = arccos(n[2])
    
    if np.abs( dip ) > 0: 

       strike = arctan2( -n[0], n[1] )
       if strike < 0: 
           strike = strike + 2 * pi

       rake = arctan2 ( - s[2], ( s[0] * cos(strike) + s[1] * sin(strike)) * sin( dip ) )

       if dip > np.pi/2:
           strike = np.pi + strike
           dip    = np.pi - dip
           rake   = np.pi - rake

    else: 
       
       print('WARNING [sl.mech.ns2sdr]: there is a trede-off between strike and rake because dip=0')
       rake = 0
       strike = - arctan2( s[1], s[0] )
       
    strike = rad2deg( strike )
    dip    = rad2deg( dip    )
    rake   = rad2deg( rake   )
      
    return strike, dip, rake


def ns2tp(n, s): 
    """ normal & slip vector to tension & pressure axis vector
    """
    
    t = (n + s) / np.sqrt(2.0)
    p = (n - s) / np.sqrt(2.0)

    return t, p


def tp2ns(t, p): 
    """ tension & pressure axis vector to normal & slip vector 
    """

    n = (t + p) / np.sqrt(2.0)
    s = (t - p) / np.sqrt(2.0)

    return n, s

def sdr2nsb(strike, dip, rake): 
    """ convert from strike, dip, rake angles to normal, slip and null vectors 
    """

    sd = sin( deg2rad(dip) )
    cd = cos( deg2rad(dip) )
    sf = sin( deg2rad(strike) )
    cf = cos( deg2rad(strike) )
    sl = sin( deg2rad(rake) )
    cl = cos( deg2rad(rake) )

    n = np.array([- sd * sf, sd * cf, - cd])
    s = np.array([cl * cf + sl * cd * sf, cl * sf - sl * cd * cf, - sl * sd]    )
    b = np.array([- sl * cf + cl * cd * sf, - sl * sf - cl * cd * cf, - cl * sd])

    return n, s, b


def tp2sdr(t, p): 
    """ convert from tension and pressure axis vectors to strike, dip, and rake angles
    """
    
    n, d = tp2ns(t, p)

    if n[2] < 0: 
        strike, dip, rake = ns2sdr(n, d)
    else:
        strike, dip, rake = ns2sdr(-n, -d)
    
    return strike, dip, rake


def moment2sdr(Mxx, Myy, Mzz, Myz, Mxz, Mxy): 
    """  moment tensor component to strike, dip, rake angles 
    """
    
    M0 = np.sqrt(Mxx**2 + Myy**2 + Mzz**2 + 2*(Myz**2 + Mxz**2 + Mxy**2)) / np.sqrt(2.0)

    # isotropic component
    tr = (Mxx + Myy + Mzz) / 3.0

    # Deviatoric Moment Tensor
    MM = np.array([[Mxx - tr, Mxy, Mxz], [Mxy, Myy-tr, Myz], [Mxz, Myz, Mzz-tr]])
    eval, evect = np.linalg.eig(MM)
    s1 = eval[0]
    s2 = eval[1]
    s3 = eval[2]
    t = evect[:,0]
    b = evect[:,1]
    p = evect[:,2]

    strike, dip, rake = tp2sdr(t, p)
    clvd = 2 * abs(s2) / max(abs(s1), abs(s3)) * 100

    return M0, strike, dip, rake, clvd

def sdr2tpb(strike, dip, rake): 
    """ strike, dip, rake angles to tension, pressure, and null vectors
    """
    
    n, s, b = sdr2nsb(strike, dip, rake)
    t, p = ns2tp(n, s)

    return t, p, b

def meca_conjugate(strike, dip, rake): 
    """ estimate strike, dip, rake angles of conjugate plane 
    """

    s1 = np.deg2rad(strike)
    d1 = np.deg2rad(dip)
    l1 = np.deg2rad(rake)

    d2 = np.arccos( np.sin(l1) * np.sin(d1) )
    l2 = np.arccos( - np.sin(d1) / np.sin(d2) * np.cos(l1) )
    s2 = s1 + np.arctan2( -np.cos(l1), -np.sin(l1) * np.cos(d1))

    if d2 > np.pi/2:
        d2 = np.pi - d2
        l2 = 2 * np.pi - l2
        s2 = np.pi + s2

    if s2 < 0.0: 
        s2 += 2*np.pi
    if s2 > 2 * np.pi:
        s2 -= 2*np.pi

    strike2 = np.rad2deg(s2)
    dip2 = np.rad2deg(d2)
    rake2 = np.rad2deg(l2)
    
    return strike2, dip2, rake2


def fault_type(strike, dip, rake):
    """ 
    Classify the fault type of given strike, dip, and rake angles based on Frohlich (1992 PEPI) classification.
    
    Args:
        strike (float): strike angle in degree
        dip (float): dip angle in degree
        rake (float): rake angle in degree
    Returns:
        str: fault type (thrust, strike-slip, normal, odd)
    """

    t, p, b = sdr2tpb(strike, dip, rake)
    plunge_th = arctan2(np.abs(t[2]), np.sqrt(t[0]**2 + t[1]**2))
    plunge_normal = arctan2(np.abs(p[2]), np.sqrt(p[0]**2 + p[1]**2))
    plunge_strike = arctan2(np.abs(b[2]), np.sqrt(b[0]**2 + b[1]**2))
    f_th = sin(plunge_th)**2
    f_nm = sin(plunge_normal)**2
    f_ss = sin(plunge_strike)**2

    typ = 'odd'
    if f_ss > 0.75: 
        typ = 'strike-slip'
    elif f_nm > 0.75:
        typ = 'normal'
    elif f_th > 0.59:
        typ = 'thrust'

    return typ