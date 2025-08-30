import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps, ImageFont

import numpy as np
import matplotlib.pyplot as plt

from tqdm import tqdm

# should work like...
# import flashplot as fp
# fp.plot()

def map_value_to_color(value, colormap='viridis'):

    norm = plt.Normalize(vmin=0, vmax=255)
    cmap = plt.get_cmap(colormap)
    color = cmap(norm(value), bytes=True)

    return color

def rescale(arr, lo: float, hi: float, vmin: float | None = None, vmax: float | None = None, end_type: type | None = None, log_scale: bool = False, nanreplace: float = 0.0):
    '''
    rescales the values in an array to fit between a range

    args:
        lo: the lower limit of the new range
        hi: the upper limit of the new range
        vmin: the lower clip bound, anything below this value is clipped and set to this value
        vmax: the upper clip bound, anything above this value is clipped and set to this value
        end_type: the final type to cast to e.g. np.uint8, np.float64
                  casts using ndarray.astype
        log_scale: use a log base 10 scale
                   note that vmin and vmax correspond to the input image value, not the log scale value

    returns:
        the rescaled array given the input

    '''

    # if vmin/vmax not set, you just choose the min max of the image
    # clip the min/max of the image if it is set
    if vmin is None:
        vmin = np.min(arr)
    else:
        arr[arr < vmin] = vmin

    if vmax is None:
        vmax = np.max(arr)
    else:
        arr[arr > vmax] = vmax

    if log_scale:
        arr[arr<0] = np.nan
        arr = np.log10(arr)
        vmin = np.log10(vmin)
        vmax = np.log10(vmax)

    scale_factor = (hi-lo)/(vmax-vmin)

    # shift from vmin to lo
    arr = arr - vmin + lo/scale_factor
    # rescales from lo to hi
    arr = arr * scale_factor

    arr = np.nan_to_num(arr, nan=nanreplace)

    if end_type is not None:
        arr = arr.astype(end_type)

    return arr

def imshow(arr, scale: float | None = None, int_scale: int | None = None, title: str | None = None, size: tuple | None = None, cmap=None, **kwargs):
    '''
    meant to replicate plt.imshow()

    args:
        arr: image array that gets rescaled from 0 to 255
        scale: the float scaling, uses lanczos resampling to scale
               this will interpolate some pixels and smooth out features slightly
        int_scale: the integer scaling using nearest neighbor resampling to scale
                   use this to preserve fine pixel details
        kwargs:
            vmin: lower clip
            vmax: upper clip
            log_scale: log scale the image
            title: add title to bottom of image
            font: font
    '''

    sy, sx = arr.shape

    arr = rescale(arr, 0, 255, end_type=np.uint8, **kwargs)

    if cmap is not None:
        arr = map_value_to_color(arr, colormap=cmap)

    image = Image.fromarray(arr)

    # used for integer factor sizing
    if int_scale is not None:
        sx = sx*int_scale
        sy = sy*int_scale
        image = image.resize((sx, sy), Image.Resampling.NEAREST)

    # float factor scaling
    if scale is not None:
        sx = sx*scale
        sy = sy*scale
        image = image.resize((int(sx), int(sy)), Image.Resampling.LANCZOS)

    if size is not None:
        image = image.resize(size, Image.Resampling.LANCZOS)

    image = image.transpose(Image.FLIP_TOP_BOTTOM)

    if title is not None:
        image = ImageOps.expand(image, border=(0,0,0,35), fill=(0))
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype('Courier New.ttf', 24)
        draw.text((10, sy+4), title, (255), font=font)

    return image

def plot(plot_xs, plot_ys, x_min=None, x_max=None, y_min=None, y_max=None, size=(300,300), padding=10):
    sy, sx = size

    rs_xs = rescale(plot_xs, padding, sx-padding, vmin=x_min, vmax=x_max)
    rs_ys = rescale(plot_ys, padding, sy-padding, vmin=y_min, vmax=y_max)

    img = Image.new('L', size)
    draw = ImageDraw.Draw(img)

    xs = [padding, sx-padding]
    lower_ys = [padding, padding]
    upper_ys = [sy-padding, sy-padding]
    draw.line(list(zip(xs,lower_ys)), fill=120, width=2) # bottom horizontal line
    draw.line(list(zip(xs,upper_ys)), fill=120, width=2) # top horizontal line

    draw.line(list(zip(rs_xs, rs_ys)), fill=255, width=2) # data

    img = img.transpose(Image.FLIP_TOP_BOTTOM)

    return img

def make_mp4(data, save_path, keep_frames=False, frames_folder='fp_frames_temp', frame_name='frame', framerate=24, use_tqdm=True, titles=None, **kwargs):
    n_places = int(np.log10(len(data))) + 1

    frames_folder = Path(frames_folder)
    frames_folder.mkdir(exist_ok=True, parents=True)

    save_paths = []

    def save_func(frame, i):
        title = None
        if titles is not None:
            title = titles[i]

        img = imshow(frame, title=title, **kwargs)

        fn = frame_name + '_' + str(i).zfill(n_places) # zfill can take a variable argument unlike fstrings

        sp = frames_folder / f'{fn}.png'
        save_paths.append(sp)
        img.save(sp)

    if use_tqdm:
        for i,frame in tqdm(enumerate(data), total=len(data)):
            save_func(frame, i)
    else:
        for i,frame in enumerate(data):
            save_func(frame, i)
    
    pattern = frames_folder / f'{frame_name}_%0{n_places}d.png'
    make_mp4_from_files(pattern, save_path, framerate)

    if not keep_frames:
        for sp in save_paths:
            sp.unlink()
        frames_folder.rmdir()

def make_mp4_from_files(pattern, save_path, framerate):
    '''
    make an mp4 file from the files given

    args:
        pattern: the filename save pattern ie: 'frame_%04d.png' corresponds to frame_0000.png, frame_0001.png, frame_0002.png, etc.
        save_path: the complete path we will be saving to
                   should end in .mp4
                   e.g. 'saveme/name.mp4'
        framerate: the framerate of the ending movie
    '''
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-r', f'{framerate:d}', '-i', f'{pattern}', '-vcodec', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-vf', 'pad=ceil(iw/2)*2:ceil(ih/2)*2', f'{save_path}'])

def show_mp4(filename):
    '''
    shows the mp4 file after its made using the lightweight ffplay player
    ffplay comes with ffmpeg!
    '''
    subprocess.run(['ffplay', '-loop', '0', filename])
