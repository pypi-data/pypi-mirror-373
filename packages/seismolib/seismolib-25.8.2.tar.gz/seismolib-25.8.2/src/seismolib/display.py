from typing import Union
from IPython import display as dd
import tempfile
import base64
import os
from pathlib import Path
from PIL import Image
import glob

def gif_movie(figs, dpi=720, crop='0.5c'): 
    
    """
    PyGMTのFigureオブジェクトのリストからGifアニメーションを作成する．Jupyter Notebook上で表示されるオブジェクトを返す．

    Parameters
    ----------
    figs : list of Figure
        PyGMTのFigureオブジェクトのリスト
    dpi : int, optional
        解像度 (default: 720)
    crop : str, optional
        余白のトリミング量 (default: '0.5c')

    Returns
    -------
    HTML : IPython.display.HTML
        Gifアニメーション
    """

    with tempfile.TemporaryDirectory() as tmpdir:
        for i, fig in enumerate(figs):
            figname = f'plot_{i:05d}.png'
            print(f'\rsaving figs ... ({(i+1)/len(figs)*100:5.1f}%)', end='')
            fig.savefig(os.path.join(tmpdir, figname), dpi=dpi, crop=crop)
        print(' Done.')
        
        cmd1 = f'ffmpeg -i {tmpdir}/plot_%5d.png '
        cmd2 = f' -vf "scale=800:-1,split [a][b];[a] palettegen [p];[b][p] paletteuse" '
        cmd3 = f' {tmpdir}/out.gif > /dev/null 2>&1'
        print(f'making gif ... ', end='')
        os.system(cmd1 + cmd2 + cmd3)
        print(' Done.')
        
        with open(f'{tmpdir}/out.gif', 'rb') as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        
    return dd.HTML(f'<img src="data:image/gif;base64,{b64}" />')
    

def show_image(fn_img, width=100):
    """
    ローカルPCの画像ファイルをJupyter Notebookに埋め込み表示する．
    PDF, JPG, GIF, SVG, BMP 形式に対応
    PDF以外はGitHubへの投稿にも対応

    Parameters
    ----------
    fn_img: 画像ファイル名．
            ipynbファイルと同じディレクトリにない場合は相対もしくは絶対パスで指定

    width: (オプション) 画像表示幅 (%)
            デフォルトは100%．PDFでは指定は無視される．
    """

    ext=os.path.splitext(fn_img)[1].lower()

    if ext == ".pdf":
        with open(fn_img, "rb") as f:
            pdf_bytes = f.read()

        # ipynb 内に base64 として埋め込まれ、ブラウザのPDFビューアで表示される
        dd.display({'application/pdf': pdf_bytes}, raw=True)
        return

    # その他画像

    with open(fn_img, 'rb') as fp:
        b64 = base64.b64encode(fp.read()).decode("ascii")
    
    srchdr = ""
    if ext == '.png':
        srchdr = 'data:image/png'
    elif ext == '.jpg' or ext == '.jpeg':
        srchdr = 'data:image/jpeg'
    elif ext == '.gif': 
        srchdr = 'data:image/gif'
    elif ext == '.svg':
        srchdr = 'data:image/svg+xml'
    elif ext == '.svg':
        srchdr = 'data:image/bmp'
    else:
        print("no such file type")
        return
   
    dd.display(dd.HTML(f'<img src="{srchdr};base64,{b64}" width="{width}%"/>'))



def show_images_as_movie(glob_pattern: Union[str, Path],
                        fps: int = 6,
                        quality: int = 95,
                        lossless: bool = False,
                        loop: int = 0,
                        width_px: int = 640):


    # 画像を収集・ソート（絶対/相対の両対応）
    paths = sorted(Path(p) for p in glob.glob(str(glob_pattern), recursive=True))
    if not paths:
        raise FileNotFoundError(f"No images matched: {glob_pattern}")

    # 読み込み & サイズ統一
    imgs = [Image.open(p).convert("RGBA") for p in paths]
    w0, h0 = imgs[0].size
    imgs = [im if im.size == (w0, h0) else im.resize((w0, h0), Image.Resampling.BILINEAR)
            for im in imgs]

    # 一時ファイルにWebP保存
    with tempfile.NamedTemporaryFile(suffix=".webp", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    duration_ms = int(1000 / max(1, int(fps)))
    imgs[0].save(
        tmp_path,
        save_all=True,
        append_images=imgs[1:],
        format="WEBP",
        duration=duration_ms,
        loop=loop,
        quality=int(quality),
        lossless=bool(lossless),
        method=6,
    )

    # base64埋め込み表示
    data_uri = "data:image/webp;base64," + base64.b64encode(tmp_path.read_bytes()).decode("ascii")
    dd.display(dd.HTML(f'<img src="{data_uri}" alt="animated webp" style="width:{int(width_px)}px;max-width:100%;height:auto;">'))

    # 一時ファイル削除
    try:
        os.remove(tmp_path)
    except Exception:
        pass
