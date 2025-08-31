import pygmt
import numpy as np
import colorsys
import datetime
import sys
import operator
import obspy
from . import geo
from . import signal

_color = ("121/046/113", "063/070/138", "052/094/042")

def _opt2str(opt):

    optstr = ""
    for key, var in opt.items():
        optstr += f"{key} = '{var}', "
    return optstr


def get_color(col, transp=None):
    """
    PyGMTのフォーマットで色を返す
    
    Parameters
    ----------
    col : str or list or tuple or int or float
        色を表す文字列，もしくはRGBのリスト，もしくは整数（色番号）
    transp : int or float
        透明度（0-100）

    Returns
    -------
    str
        PyGMTの色表現    
    """
    if isinstance(col, (int, float)):
        c = _color[int(col) % len(_color)]
    elif isinstance(col, (list, tuple)):
        c = f"{int(np.round(col[0])):03d}/{int(np.round(col[1])):03d}/{int(np.round(col[2])):03d}"
    else:
        c = str(col)

    if transp is not None:
        c += "@" + str(transp)

    return c


def hsv2rgb(h, s=1, v=1):

    """
    HSV to RGB conversion
    
    Parameters
    ----------
    h : float
        Hue (0-360)
    s : float
        Saturation (0-1)
    v : float
        Value (0-1)
    
    Returns
    -------
    str
        RGB color in PyGMT format
    """
    rgb = colorsys.hsv_to_rgb(h, s, v)
    r = rgb[0] * 255
    g = rgb[1] * 255
    b = rgb[2] * 255

    return get_color((r, g, b))


def get_pen(width, col, transp=None, dash=None):
    """
    Return pen type in PyGMT format

    Parameters
    ----------
    width : float or str
        Pen width
    col : str or list or tuple or int or float
        Pen color
    transp : int or float
        Transparency (0-100; Default: None)
    dash : str
        Dash style (Default: None)
    """

    if isinstance(width, (int, float)):
        width = str(width) + "p"

    pentype = width + "," + get_color(col, transp)

    if dash is not None:
        pentype += "," + dash

    return pentype


def get_font(fontsize, font, col="Black", transp=None):
    """
    Return font specification in PyGMT format

    Parameters
    ----------
    fontsize : int or str
        Font size   
    font : str
        Font
    col : str or list or tuple or int or float
        Font color
    transp : int or float

    """

    if isinstance(fontsize, int):
        fontsize = str(fontsize) + "p"

    fontspec = fontsize + "," + font + "," + get_color(col, transp)

    return fontspec


def pygmt_config(out=False):
    """
    標準的なGMT設定．

    Parameters
    ----------
    out : bool
        Trueの場合は，設定文字列を返す．デフォルトは False

    Example
    -------

    with pygmt_config():
        fig.XXX()
        
    のように with 句と使う．
    """

    conf = """pygmt.config(
        FONT_ANNOT_PRIMARY="12p,Helvetica,black",
        FONT_ANNOT_SECONDARY="11p,Helvetica,black",
        FONT_LABEL="14p,Helvetica,black",
        FONT_TITLE="16p,Helvetica,black",
        MAP_GRID_PEN_PRIMARY="0.25p,30/30/30,.",
        MAP_FRAME_TYPE="plain",
        FORMAT_GEO_MAP="DF",
        FORMAT_FLOAT_OUT="%.4g",
        PS_IMAGE_COMPRESS="none",
        PS_LINE_CAP="round",
        PS_LINE_JOIN="round")"""

    if out:
        return conf
    else:
        return pygmt.config(
            FONT_ANNOT_PRIMARY="12p,Helvetica,black",
            FONT_ANNOT_SECONDARY="11p,Helvetica,black",
            FONT_LABEL="14p,Helvetica,black",
            FONT_TITLE="16p,Helvetica,black",
            MAP_GRID_PEN_PRIMARY="0.25p,30/30/30,.",
            MAP_FRAME_TYPE="plain",
            FORMAT_GEO_MAP="DF",
            FORMAT_FLOAT_OUT="%.4g",
            PS_IMAGE_COMPRESS="none",
            PS_LINE_CAP="round",
            PS_LINE_JOIN="round",
        )


def pygmt_config_S():
    """
    標準的なGMT設定．(Small igure version)

    Parameters
    ----------
    out : bool
        Trueの場合は，設定文字列を返す．デフォルトは False

    Example
    -------

    with pygmt_config():
        fig.XXX()
        
    のように with 句と使う．
    """

    return pygmt.config(
        FONT_ANNOT_PRIMARY="8p,Helvetica,black",
        FONT_ANNOT_SECONDARY="6p,Helvetica,black",
        FONT_LABEL="9p,Helvetica,black",
        FONT_TITLE="9p,Helvetica,black",
        MAP_GRID_PEN_PRIMARY="0.25p,30/30/30,.",
        MAP_FRAME_TYPE="plain",
        FORMAT_GEO_MAP="DF",
        FORMAT_FLOAT_OUT="%.4g",
        PS_IMAGE_COMPRESS="none",
        PS_LINE_CAP="round",
        PS_LINE_JOIN="round",
    )


def plot(x,
         y,
         size=(12, 12),
         region=None,
         labels=None,
         symbol="-",
         axis=("lin", "lin"),
         title=None,
         show_script=False):

    """
    Easy plot by using pyGMT

    Parameters
    ----------
    x : array-like
        独立変数
    y : array-like (or tuple of array-like)
        従属変数．
        同じ独立変数に対する複数の従属変数を `(y1, y2)` のようにタプルで与えられる．
    region : array or tuple
        (xmin, xmax, ymin, ymax) ．デフォルトでは自動設定．
    labels : list
        [x軸ラベル, y軸ラベル]
    title : str
        プロットタイトル（上部に表示）
    symbol : str
        デフォルト（'-'）で線，それ以外で◯．他のシンボルは未対応
    axis : array (or tuple) of str
        x軸とy軸それぞれ 'lin' or 'log' で軸の線形か対数かを指定．デフォルトは線形．
    show_script : bool
        自動生成したスクリプトを表示する．デフォルトは False
    
    """

    import pygmt
    import numpy as np

    y = np.array(y)
    x = np.array(x)

    ## projection
    proj = "X"
    proj_X = f"{size[0]}c"
    if axis[0] == "log":
        proj_X += "l"
    proj_Y = f"{size[1]}c"
    if axis[1] == "log":
        proj_Y += "l"
    projection = proj + proj_X + "/" + proj_Y

    if region is None:
        if axis[0] == "log":
            xmin = np.nanmin(x[(x > 0)]) * 0.9
        else:
            xmin = np.nanmin(x) - (np.nanmax(x) - np.nanmin(x)) * 0.1
        xmax = np.nanmax(x) + (np.nanmax(x) - np.nanmin(x)) * 0.1
        if axis[1] == "log":
            ymin = np.nanmin(y[(y > 0)]) * 0.9
        else:
            ymin = np.nanmin(y) - (np.nanmax(y) - np.nanmin(y)) * 0.1
        ymax = np.nanmax(y) + (np.nanmax(y) - np.nanmin(y)) * 0.1

        region = [xmin, xmax, ymin, ymax]

    frame_axis = "WSen"
    if title is not None:
        frame_axis += "+t" + title

    xframe = "xafg"
    yframe = "yafg"
    if axis[0] == "log":
        xframe = "xa1f2g1p"
    if axis[1] == "log":
        yframe = "ya1f2g1p"

    if labels is not None:
        if len(labels[0]) > 0:
            xframe += '+l' + labels[0]
        if len(labels[1]) > 0:
            yframe += '+l' + labels[1]
    frame = [frame_axis, xframe, yframe]

    if show_script:
        print(f"fig = pygmt.Figure()\n")
        print(f"with {pygmt_config(out=True)}: \n")
        print(f"    fig.basemap(projection='{projection}', ")
        print(f"                region={region}, ")
        print(f"                frame={frame})")

    ## Plot
    fig = pygmt.Figure()

    optarg = {}
    if symbol == "-":
        optarg["pen"] = get_pen("thick", 0)
    else:
        optarg["style"] = "c0.2c"
        optarg["pen"] = get_pen("default", "black")
        optarg["fill"] = get_color(0)

    with pygmt_config():

        fig.basemap(projection=projection, region=region, frame=frame)

        if len(np.array(y).shape) == 1:
            fig.plot(x=x, y=y, **optarg)
            if show_script:
                print(f"    fig.plot(x=x, y=y,")
                print(f"             {_opt2str(optarg)})")
        else:
            for i in range(np.array(y).shape[0]):
                if symbol == "-":
                    optarg["pen"] = get_pen("thick", i)
                else:
                    optarg["fill"] = get_color(i)

                fig.plot(x=x, y=y[i,:], **optarg)
                if show_script:
                    print(f"    fig.plot(x=x, y=y[{i},:],")
                    print(f"             {_opt2str(optarg)})")

    if show_script:
        print("fig.show()")

    return fig



def xyz2grd(x, y, z, region=None, dx=None, dy=None):

    """
    Convert xyz data to grd data by usin PyGMT.xyz2grd module

    Parameters
    ----------
    x, y: array-like
        independent variable arrays x[nx], y[ny]
    z: array-like
        two-dimensional array
        z[nx,ny]
    region: array-like or str
        GMT's region setting (automatically detemined by default)

    Return
    ------
    pygmt.grddata

    """

    if dx is None:
        dx = x[1] - x[0]
    if dy is None:
        dy = y[1] - y[0]
    if region is None:
        region = (x[0], x[-1], y[0], y[-1])

    data = [[x[i], y[j], z[i, j]] for i in range(len(x)) for j in range(len(y))]
    spacing = str(dx) + "/" + str(dy)

    return pygmt.xyz2grd(data=data, region=region, spacing=spacing)


def surface(x, y, z, region=None, dx=None, dy=None, tension=0.0):

    """
    Convert xyz data to grd data by usin PyGMT.surface module

    Parameters
    ----------
    x, y: array-like
        independent variable arrays x[nx], y[ny]
    z: array-like
        two-dimensional array
        z[nx,ny]
    region: array-like or str
        GMT's region setting (automatically detemined by default)
    dx, dy: float
        grid spacing. default is x[1]-x[0] and y[1]-y[0]
    tension: float
        tension parameter of PyGMT.surface
        
    Return
    ------
    pygmt.grddata
    
    """
    if dx is None:
        dx = x[1] - x[0]
    if dy is None:
        dy = y[1] - y[0]

    if region is None:
        region = (min(x), max(x), min(y), max(y))

    if len(z.shape) == 2:
        data = [[x[i], y[j], z[i, j]] for i in range(len(x)) for j in range(len(y))]
    else:
        data = [[x[i], y[i], z[i]] for i in range(len(x))]

    spacing = str(dx) + "/" + str(dy) 
    return pygmt.surface(
        data = data, 
        region = region, 
        spacing = spacing, 
        tension = tension)


def wiggleplot(stream, timrange, xlabel='time [s]', ylabel='traces'): 
    
    """
    Wiggle plot of the seismogram. 
    
    Note
    ----
    the detailed documentation will be available later. 
    """
    s = stream[0]
    b = np.floor(s.stats.sac.b*10000+0.5)/10000
    e = np.floor(s.stats.sac.e*10000+0.5)/10000    
    dt = np.floor(s.stats.sac.delta*10000+0.5)/10000
    tim = np.arange(b, e+dt, dt)

    fig = pygmt.Figure()
    base = np.zeros(tim.size)
    for i, s in enumerate(stream): 
        fig.wiggle(x = tim, y = base+i, z = s.data, projection='X16c/8c', color = ["200/100/100@30+p", "100/100/200@30+n"], region=[timrange[0], timrange[1], -1, len(stream)], scale=1/len(stream)/2)
    
    fig.basemap(frame=['WSen', 'xaf+l'+xlabel, 'yaf+l'+ylabel])
    fig.show(width=800)


def _magnitude_size(m): 
    return 0.03 + 0.01 * (2**m)


def eqplot(df, region=None, dep=None, xsize=12, zsize=5, magsize=_magnitude_size, cmap = 'roma', zdiv = 5): 

    """ 
    地震活動の断面図プロットを作成する．
    magsize には マグニチュードからサイズ（cm）への変換を行う関数を与える．

    Parameters
    ----------
    df : pandas.DataFrame
        地震カタログデータフレーム．longitude, latitude, depth, magnitude の列を持つ必要がある．
    region : array-like
        [lon0, lon1, lat0, lat1] の順で与える．デフォルトはデータフレームの範囲．
    dep : array-like
        [z0, z1] の順で与える．デフォルトはデータフレームの範囲．
    xsize : float
        横幅（cm）
    zsize : float
        高さ（cm）
    magsize : function
        マグニチュードからサイズ（cm）への変換関数
    cmap : str
        カラーマップ名
    zdiv : int
        カラーマップの深さ方向の分割数
    """
    
    if region is None: 
        region = [min(df.longitude), max(df.longitude), 
                  min(df.latitude), max(df.latitude)]
    
    fig = pygmt.Figure()

    if dep is None:
        dep = [min(df.depth), max(df.depth)]
    
    z0 = dep[0]
    z1 = dep[1]
    dz = (dep[1] - dep[0]) / zdiv
    lon0 = region[0]
    lon1 = region[1]
    lat0 = region[2]
    lat1 = region[3]

    df2 = df.query('@lon0 <= longitude <= @lon1')\
            .query('@lat0 <= latitude  <= @lat1')\
            .query('@z0   <= depth     <= @z1')\

    ysize = geo.mercator_aspect(region) * xsize
    
    pygmt.makecpt(
        cmap         = cmap,       
        series       = [z0, z1, dz], 
        background   = True,         
        continuous   = True, 
        transparency = 40    
    )

   
    with pygmt_config():

        fig.coast(
            projection=f'X{xsize}c/{ysize}c', 
            region = region, 
            frame = ['WseN', 'xaf', 'yaf'], 
            resolution = 'h', 
            area_thresh=100, 
            shorelines = 'default,black', water='230')

        fig.plot(
            x     = df2.longitude,
            y     = df2.latitude,
            style = 'c',         
            pen   = 'faint,black', 
            size  = magsize(df2.magnitude),
            cmap  = True,                            
            fill = df2.depth, 
            transparency = 40)

        fig.shift_origin(0, -6)

        fig.plot(
            projection = f'X{xsize}c/-{zsize}c', 
            region = [lon0, lon1, z0, z1], 
            x     = df2.longitude,
            y     = df2.depth,
            style = 'c',         
            pen   = 'faint,black', 
            size  = magsize(df2.magnitude), 
            cmap  = True,                             
            fill = df2.depth,
            frame = ['WSen', 'xaf+llongitude [deg.]', 'yaf+ldepth [km]'] ,
            coltypes = 'i0x,1f', 
            transparency = 40 )

        fig.shift_origin(13, 6)

        fig.plot(
            projection = f'X{zsize}c/{ysize}c', 
            region = [z0, z1, lat0, lat1], 
            x = df2.depth, 
            y = df2.latitude, 
            style = 'c',         
            pen   = 'faint,black', 
            size  = magsize(df2.magnitude), 
            cmap  = True,                             
            fill = df2.depth,
            frame = ['wSEen', 'xaf+ldepth [km]', 'yaf+llatitude [deg]'], 
            coltypes = 'i0f,1y', 
            transparency = 40 )

        fig.shift_origin(0, -0.5)
        fig.colorbar(position = '+e')

        fig.shift_origin(0, -zsize)

        fig.plot(x = [1, 3, 5, 7], y = [2, 2, 2, 2], 
                 region = [ 0, 8, 0, 4], projection=f'X{zsize}c/2c',
                 size=magsize(np.array([0, 2, 4, 6])), style='c', 
                 pen='thin,black')
        fig.text(x=[1, 3, 5, 7], y = [0.5, 0.5, 0.5, 0.5], justify='CT', 
                 text=['M0', 'M2', 'M4', 'M6'], 
                 font='8p,Helvetica,Black')

    return fig


def record_section(stream, dist=None, tim=None, size = (20, 12), 
                   decimation=1, transparency=0, orientation='horizontal', 
                   otim = None, filt = 'raw', fc = None, nord=2, twopass=True, 
                   scale = 'auto', mag = 1.0, 
                   color = ("134/49/74", "85/80/39", "63/70/138", "111/47/127", "44/86/105"),
                   plot_stcode=False, reduce = None, azimuth = [0, 360]):

    """ Plot record section of the seismogram: PyGMT version
    
    簡易プロットで良いなら，`obspy.Stream.plot(type='section')` のほうが高速に動作する．
    
    Parameters
    ----------
    stream : obspy.Stream
        地震波形データ．
        その中のTraceにstats.distance (m) もしくは stats.sac.dist (km) が入っていることが前提
    dist : array-like (optional)
        プロットする距離範囲 (km) の下限と上限を list か tuple で与える．
        デフォルトはstreamに含まれる距離の最小値から最大値まで
    tim : array-like (optional)
        プロットする時間範囲 (s) の下限と上限を list か tuple で与える．
        デフォルトはstreamに含まれる時間の最小値から最大値まで
    size : array-like (optional)
        `(width, height)` を cm 単位で与える．デフォルトは `(20, 12)`
    decimation : int (optional)
        プロットを高速化するために，波形をdecimationごとに間引いてプロットする．
        たとえばdecimation=10なら波形の 0, 10, 20 ... サンプルが飛び飛びにプロットされる．
        デフォルトは1（間引きなし）.
        1つの地震波形のサンプル数が数千程度以下におさまる程度にするのがよい．サンプル数が多くなると極端に遅くなる．
    transparency : int (optional)
        波形の透明度．0-100の数値で与える．デフォルトは0（不透明）
    orientation : 'horizontal' or 'vertical'
        horizontal は 横軸に距離，縦軸に時間（デフォルト：ObsPyと同じ），vertical はその逆
    otim : datetime.datetime (optional)
        時刻 0 の時間（地震発生時刻）を強制的に otim にずらす
        デフォルトでは trace.stats.starttime を 時間 t = trace.stats.sac.b のであるとして，t=0 
        に相当する時刻がotimに相当する．これは，eventdataの仕様に合わせてある．
    filt : 'raw', 'bp' ,'lp' , 'hp' (optional)
        フィルタの種類．デフォルトは 'raw' （生波形=なにもしない）．
        bp の場合には fc = (fl, fh) で低周波と高周波の下限上限を Hz で，
        lp と hp の場合には fc に上限もしくは下限の周波数を Hz で，それぞれ与える．
    fc : フィルタの周波数パラメタ．(optional)
        `filt` パラメタの説明参照．
    nord : int (optional)
        フィルタの次数．デフォルトは 2 
    twopass: Bool (optional)
        前後からのゼロ位相フィルタを適用するかどうか．デフォルトはTrue
        Trueの場合，フィルタが2回適用されるため，フィルタ次数は `nord * 2` になる．
    scale : 'auto' or flort (optional)
        'auto' の場合，波形ごとの最大値で規格化される．
        数値で与えられた場合，波形の単位におけるその数値が基準振幅となる．デフォルトは'auto'
    mag : float (optional)
        scaleで指定された倍率を全体に `mag` 倍する．主に'auto'のときに全体の倍率を調整する用途．
        デフォルトは 1
    color : array-like of str or str(optional)
        波形の色．単一の文字列で与えられたとき（例：'black'）はすべてその色になる．
        list/tupleで与えられたとき（['black', 'blue', 'red', 'orange']）波形の色はリスト内の
        色を周期的に用いる．
        デフォルトは ("134/49/74", "85/80/39", "63/70/138", "111/47/127", "44/86/105")
    plot_stcode : Bool (optional)
        観測点名をプロットする場合 True にする．デフォルトはFalse
    reduce : float (optional)
        数値が与えられたとき，それを km/s 単位のレデュース速度とみなして波形をレデュースする．
        デフォルトは None （レデュースしない）
    azimuth : array-like
        (az1, az2) という長さ2のlist/tupleが与えられたとき，震源から見た観測点の方位角（Azimuth）が
        az1 <= azimuth < az2 の観測点だけプロットする．
    """
    
    
    if not isinstance(color, (list, tuple)): 
        color = [color]

    ## まず距離と時間の範囲を取得する
    dmin = 1e30
    dmax = -1.0 
    tmin = datetime.datetime(2100, 3, 5, 1, 2, 4, 0)
    tmax = datetime.datetime(1, 1, 1, 0, 0, 0)

    for tr in stream: 
        # 震央距離は stats.distance (m) or stats.sac.dist (km) のどちらかをとる
        try: 
            d = tr.stats.distance / 1000
        except:
            d = tr.stats.sac.dist
            tr.stats.distance = d * 1000

        tb = tr.stats.starttime.datetime
        te = tr.stats.endtime.datetime
        otim_ = tb - datetime.timedelta(seconds = float(tr.stats.sac.b))

        if otim is None:
            otim = otim_

        dmin = min(dmin, d)
        dmax = max(dmax, d)
        tmin = min(tmin, tb)
        tmax = max(tmax, te)

        title = tr.stats.sac.kevnm

    if dist is not None:
        dmin = dist[0]
        dmax = dist[1]

    if orientation == 'horizontal' :
        Lx = size[0]
    else:
        Lx = size[1]

    csize=f"{size[0]}c/{size[1]}c"
    projection = 'X' + csize

    fig = pygmt.Figure()

    tmin_s = (tmin - otim).total_seconds()
    tmax_s = (tmax - otim).total_seconds()

    if tim is not None:
        tmin_s, tmax_s = tim

    if orientation == 'horizontal': 
        region = [dmin, dmax, tmin_s, tmax_s]
    else:
        region = [tmin_s, tmax_s, dmin, dmax]

    # confirm filter parameter
    if filt.lower() == 'bp': 
        if isinstance(fc, (list, tuple)): 
            assert( fc[0] <= fc[1] )
        else:
            print('invalid filter parameter', file=sys.stderr)
            filt = 'raw'

    elif filt.lower() == 'lp': 
        if not isinstance(fc, (float, int)): 
            print('invalid filter parameter', file=sys.stderr)
            filt = 'raw'

    elif filt.lower() == 'hp':
        if not isinstance(fc, (float, int)): 
            print('invalid filter parameter', file=sys.stderr)
            filt = 'raw'  

    unit = 'nm/s'
    with pygmt_config():

        itr = 0

        for tr in sorted(stream, key=operator.attrgetter('stats.distance')):

            d = tr.stats.distance / 1000

            if d < dmin or dmax < d: 
                continue

            if not azimuth[0] <= tr.stats.sac.az <= azimuth[1]:
                continue

            dat = signal.rmean(tr.data)
            
            signal.rmean(dat)
            signal.taper_cosine(dat, int(len(dat)*0.025))

            # filter
            if filt.lower() == 'bp':
                dat = signal.bp(dat, tr.stats.sampling_rate, fc[0], fc[1], nord, twopass)
            elif filt.lower() == 'hp':
                dat = signal.hp(dat, tr.stats.sampling_rate, fc, nord, twopass)
            elif filt.lower() == 'lp':
                dat = signal.lp(dat, tr.stats.sampling_rate, fc, nord, twopass)

            tim_s = tr.times() + tr.stats.sac.b
            if reduce is not None:
                tim_s = tim_s - d / reduce

            mask = (tmin_s <= tim_s) & (tim_s <=tmax_s)
            maxv = np.max(np.abs(dat[mask]))

            rscale = 1
            if scale == 'auto':                
                rscale = (dmax - dmin) / Lx  * mag / maxv / 2
            else:
                rscale = (dmax - dmin) / Lx / scale 

            if orientation == 'horizontal': 

                fig.plot(projection = projection, 
                        region = region, 
                        x = d + dat[::decimation] * rscale, 
                        y = tim_s[::decimation], 
                        pen=f'default,{color[itr%len(color)]}', 
                        transparency=transparency)
            else:
                fig.plot(projection = projection, 
                        region = region, 
                        y = d + dat[::decimation] * rscale, 
                        x = tim_s[::decimation], 
                        pen=f'default,{color[itr%len(color)]}', 
                        transparency=transparency)

            if plot_stcode: 
                if orientation == 'horizontal': 
                    fig.text(x=d, y = tmax_s + (tmax_s-tmin_s)*0.01, no_clip=True, 
                             text=tr.stats.station, angle=90, justify='LM', 
                             font='6p,Courier,Black' )
                else:
                    fig.text(x=tmax_s + (tmax_s-tmin_s)*0.01, y=d, no_clip=True, 
                             text = tr.stats.station, angle=0, justify='LM', 
                             font='6p,Courier,Black' )
    

            itr += 1


        if reduce is not None:
            timlabel = f'reduced time [s] with v@-red@-={reduce} km/s'
        else:
            timlabel = 'elapsed time [s]'

        if orientation == 'horizontal': 

            fig.basemap(projection = projection, 
                    region = region, 
                    frame = [f'WSen', 'xafg+ldistance [km]', f'yafg+l{timlabel}'], 
                    )
        else:
            fig.basemap(projection = projection, 
                    region = region, 
                    frame = [f'WSen', f'xafg+l{timlabel}', 'yafg+ldistance [km]'], 
                    )

        # event information

        if orientation=='horizontal' and plot_stcode: 
            fig.shift_origin(0, size[1]+1.5)
        else:
            fig.shift_origin(0, size[1]+0.5)

        if filt == 'raw': 
            cfilt = 'raw data'
        elif filt == 'bp':
            cfilt = f'{fc[0]} <= f <= {fc[1]} Hz (nord={nord}, two-pass={twopass})'
        elif filt == 'lp':
            cfilt = f'f <= {fc} Hz (nord={nord}, two-pass={twopass})'
        elif filt == 'lp':
            cfilt = f'f >= {fc} Hz (nord={nord}, two-pass={twopass})'

        fig.text(projection='X10c/2c', region=[0, 10, 0, 5 ], 
                 x=0, y=3,
                 text = f"Event ID: {stream[0].stats.sac.kevnm}", 
                 no_clip=True, justify='LB', font='8p,Courier,Black')
        fig.text(x=0, y=2, 
                 text = "Origin time: "+otim.strftime("%Y-%m-%d %H:%M:%S"),
                 no_clip=True, justify='LB', font='8p,Courier,Black')
        fig.text(x=0, y=1,
                 text = f"{cfilt}", 
                 no_clip=True, justify='LB', font='8p,Courier,Black')
        fig.text(x=0, y=0,
                 text = f"{azimuth[0]} <= azimuth <= {azimuth[1]}", 
                 no_clip=True, justify='LB', font='8p,Courier,Black')                

        fig.shift_origin(0, -size[1])
        if isinstance(scale, (int, float)): 

            if orientation == 'horizontal':         
                fig.shift_origin(size[0]+0.25, 0)
                fig.plot(projection='X2c/2c', region=[0, 2, 0, 2], 
                        x = [0.5, 1.5], y = [0.1, 0.1], 
                        pen = 'thicker,black')
                fig.text(x=1, y=0.25, justify='CB', 
                        text=f'{scale/1e6} mm/s', font='8pt,Courier')
            else:
                fig.shift_origin(size[0]+1.25, 0)
                fig.plot(projection='X2c/2c', region=[0, 2, 0, 2], 
                        x = [0.1, 0.1], y = [0.5, 1.5], 
                        pen = 'thicker,black')
                fig.text(x=0.25, y=1, justify='CT', 
                        text=f'{scale/1e6} mm/s', angle=90, font='8pt,Courier')

    return fig


def spectrogram(trace, nwin=512, wshift=100, nfft=None, 
                frange=None, trange=None, 
                prange=None, flog=True, plog=True, 
                cmap='abyss', cmap_cont=True, 
                return_data=False): 
    
    """
    Plot spectrogram of a given trace. 
    
    Parameters
    ----------
    trace: Obspy trace (or stream)
        if this is stream, use trace[0] data.
        trace must contain `trace.stats.delta` and `trace.stats.npts` headers.
    nwin: int
        length of time window to estimate spectrum, in number of samples.
    wshift: int
        length of time shift to calculate spectorgram, in number of samples.
    nfft: int
        length of time window length to perform FFT, in number of samples .
        nfft must be equall or larger than nwin. 
        It is most computationally efficient if nfft is power of 2
        (like 256, 512, 1024 ... )
    frange: list of two float numbers
        frequency range to be plotted. Given in (f_minimum, f_maximum)
        if it is None (default), frequency range is automatically detemined 
        by using nfft and sampling interval of trace. 
    trange: list of two float numbers
        temporal range to be plotted. 
        if it is None (default), temporal range is automatically detemined 
        by using length of the given trace. 
    prange: list of two float numbers
        minimum and maximum of the colar pallete. 
    flog: Bool
        Plot frequency axis in logarithmic scale. True for default. 
    plog: Bool
        Plot power spectral density function (color) in logarithmic scale. True for default. 
    cmap: str
        Specify color map. Default is 'abyss'
    cmap_cont: Bool
        Use continuous color palette. Default is True. 
    return_data: Bool
        if this value is set to True, this funciton returns (fig, time, frequency, PSDF)

    Returns
    -------
    fig: PyGMT.Figure
        PyGMT figure object.
    time: array
        time axis of the spectrogram
    frequency: array
        frequency axis of the spectrogram
    PSDF: array

    """
    
    if type(trace) is obspy.core.stream.Stream:
        trace = trace[0]

    dt   = trace.stats.delta
    npts = trace.stats.npts
    
    # 特段の指定がないときにはFFT長=window長
    if nfft is None : 
        nfft = nwin
    if nfft < nwin: 
        print("[spectrogram] nfft >= nwin is required. Reset nfft=nwin")
    
    t, f, p = _calc_spectrogram(trace.data, dt, npts, nwin, nfft, wshift)
    fig = _plot_spectrogram(t, f, p, trace, 
                            frange, trange, prange, flog, plog, 
                            cmap, cmap_cont)
    
    if return_data: 
        return fig, t, f, p
    else:
        return fig

def _calc_spectrogram(u, dt, npts, nwin, nfft, wshift): 
    
    p = []
    t = []
    for ic in range(nwin//2, npts-nwin//2, wshift): 

        ib = ic - nwin // 2
        ie = ib + nwin - 1
        
        t.append((ib + ie) / 2 * dt)
        
        _p, f = signal.psdf_fft(u[ib:ie], dt, nfft=nfft)

        p.append(_p)

    return np.array(t), np.array(f), np.array(p)


def _plot_spectrogram(t, f, p, u, frange=None, trange=None, 
                      prange=None, flog=True, plog=True, 
                      cmap='abyss', cmap_cont=True): 
    
    if frange is None: 
        if flog:
            frange = [f[1], f[-1]]
        else: 
            frange = [f[0], f[-1]]
    
    if trange is None:
        trange = [t[0], t[-1]]
    
    fig = pygmt.Figure()
    
    grid = surface(t, f, p)

    if prange is None: 
        if plog: 
            prange = [np.max(p)/1e8, np.max(p)]
        else:
            prange = [np.max(p)/100, np.max(p)]

    if plog: 
        series = [np.log10(prange[0]), np.log10(prange[1]), 1]
    else: 
        dp = (prange[1] - prange[0]) / 5
        series = [prange[0], prange[1]]
        
    pygmt.makecpt(cmap=cmap, log=plog, series=series, continuous=cmap_cont)

    projection = 'X14c/8c'
    if flog:
        projection += 'l'
    
    xframe = f'xaf+lElapsed time [s]'
    if flog:
        yframe = f'ya1f2p+lFrequency [Hz]'
    else:
        yframe = f'yaf+lFrequency [Hz]'
    
    fig.grdimage(projection=projection, 
                 grid = grid, 
                 region= (trange[0], trange[1], frange[0], frange[1]), 
                 frame=['WSen', xframe, yframe])
    
    unit = [ None, None , None , None , None, None, 
            'nm@+2@+/Hz', '(nm/s)@+2@+/Hz', '(nm/s@+2@+)@+2@+/Hz']
    try: 
        uunit = unit[u.stats.sac.idep]
    except: 
        uunit = 'relative'
    
    if plog: 
        pframe = f'xa1f1p+lPSDF [{uunit}]'
    else:
        pframe = f'xaf+lPSDF [{uunit}]'
        
    fig.colorbar(log=plog, 
                 frame=[pframe], 
                 position='JRM+w8c/0.5c+o0.4c/0c')

    fig.shift_origin(0, 8.5)
    fig.plot(x=u.times(), y=u.data, 
             pen='thinner,black', projection='X14c/2.5c', 
             region = [trange[0], trange[1],
                      -np.max(np.abs(u.data)),np.max(np.abs(u.data))], 
             frame=['E', 'x', f'ya{np.max(np.abs(u.data))}'])
    
    try: 
        stinf = f'{u.stats.sac.kstnm} ({u.stats.sac.kcmpnm}) '
        stinf += u.stats.starttime.strftime("%Y-%m-%d %H:%M:%S")
        
    except:
        stinf = f'{u.stats.station} ({u.stats.channel}) '
        stinf += u.stats.starttime.strftime("%Y-%m-%d %H:%M:%S")
    
    fig.shift_origin(0, 2.5)
    fig.text(projection='X14c/2c', region=(0, 14, 0, 2),
             x=0, y=0.1, text=stinf, font='12p,Helvetica,Black', 
             justify='LB')
    
    return fig


def plot_meca(strike, dip, rake, azimuth=None, takeoff=None, polarization=None,
              compressionfill='250/50/150@50', polarizationfill='red',
              grid=False):

    """
    Plot focal mechanism with azimuth, takeoff and polarization

    Parameters
    ----------
    strike, dip, rake: floats
        Strike, dip and rake angles of the focal mechanism
    azimuth, takeoff, polarization: list of floats (optional)
        Azimuth, takeoff and polarization angles of the radiation pattern
        if these lists are not provided, only the focal mechanism is plotted.
    compressionfill: str
        Fill color for the compression quadrants
    polarizationfill: str
        Fill color for the observation points with compressional polarity
    grid: Bool
        Plot grid on the focal mechanism plot
    """

    fig = pygmt.Figure()

    if strike < 0: 
        fig.meca(spec={"mrr":2.897, "mtt": 2.897, "mff": 2.897, 
                       "mrf": 0, "mrt":0, "mtf":0, "exponent": 23},
                scale='10c', 
                longitude=0, latitude=0, 
                projection ='X11c/11c', region=[-1.1, 1.1, -1.1, 1.1], 
                compressionfill='white', 
                pen = 'thin,black')
        
        if grid: 
            fig = _plot_mech_grid(fig)
                           
    else:
        fig.meca(spec={"strike":strike, "dip": dip, "rake": rake, "magnitude": 5},
                scale='10c', 
                longitude=0, latitude=0, 
                projection ='X11c/11c', region=[-1.1, 1.1, -1.1, 1.1], 
                compressionfill=compressionfill, 
                outline='thin,black')
        if grid: 
            fig = _plot_mech_grid(fig)
        

    if azimuth is None or takeoff is None or polarization is None: 
        return fig

    if len(azimuth) != len(takeoff) or len(azimuth) != len(polarization): 
        return fig

    for a, t, p in zip(azimuth, takeoff, polarization):

        if t >= 90: 
            a += 180
            t = 180 - t

        aa = np.deg2rad(a)
        rr = np.sqrt(2) * np.sin(np.deg2rad(t)/2) # 等積投影公式

        xx = rr * np.sin(aa)
        yy = rr * np.cos(aa)

        if p > 0: 
            col = polarizationfill
        else:
            col = 'white'
 
        fig.plot(projection ='X11c/11c', region=[-1.1, 1.1, -1.1, 1.1], 
                 x = xx, y = yy, style = 'c0.2c', fill=col, pen='faint,black')


    return fig

def _plot_mech_grid(fig):
    
    for theta in np.arange(10, 90, 10):
        r = np.sqrt(2) * np.sin(np.deg2rad(theta)/2)
        phi = np.linspace(0, 2*np.pi, 200)
        xx = r*np.cos(phi)
        yy = r*np.sin(phi)
        fig.plot(projection ='X11c/11c', region=[-1.1, 1.1, -1.1, 1.1], 
                x = xx, y = yy, pen='thin,100', transparency=70)

    for phi in np.arange(0, 180, 30):
        x1 = np.cos(np.deg2rad(phi))
        y1 = np.sin(np.deg2rad(phi))
        x2 = np.cos(np.deg2rad(phi+180))
        y2 = np.sin(np.deg2rad(phi+180))
        fig.plot(projection ='X11c/11c', region=[-1.1, 1.1, -1.1, 1.1], 
                x = [x1, x2], y = [y1, y2], pen='thin,100', transparency=70)  
        
    return fig

