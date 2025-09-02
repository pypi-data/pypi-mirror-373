import matplotlib; matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import math
import gc
import cv2

def auto_sized_figure (imgs, rows, cols):
    h, w = imgs [0].shape [:2]
    fw = int (w * cols / 16)
    fh = int (h * rows / 16)
    if fw > 16:
        fh = fh * 16 / fw
        fw = 16
    fig = plt.figure (figsize = (fw, fh))
    return fig

def gview (cols, *imgs, saveas = None, titles = None, axis = True, dpi = 100, brg = True):
    if len (imgs) == 1 and isinstance (imgs [0], list):
        imgs = imgs [0]

    if len (imgs) % cols != 0:
        lacks = cols - (len (imgs) % cols)
        if lacks:
            for _ in range (lacks):
                dummy = np.zeros_like (imgs [-1], dtype = np.uint8)
                dummy [:] = 255
                imgs.append (dummy)
                titles and titles.append ('')

    rows = math.ceil (len (imgs) // cols)
    fig = auto_sized_figure (imgs, rows, cols)
    for i, img in enumerate (imgs):
        if brg:
            img = cv2.cvtColor (img, cv2.COLOR_BGR2RGB)
        ax1 = fig.add_subplot(rows, cols, i + 1)
        if img.dtype == np.uint8:
            img = np.clip (img, 0, 255)
        else:
            img = np.clip (img, 0, 1)

        if len (img.shape) == 2:
            img = np.expand_dims (img, axis = -1)
        if img.shape [-1] == 1:
            img = np.repeat (img, 3, -1)
        if titles:
            ax1.set_title (titles [i])
        if not axis:
            ax1.axis ('off')
        ax1.imshow (img)

    if saveas:
        plt.tight_layout ()
        plt.savefig (saveas, dpi = dpi, facecolor='#eeeeee')
    else:
        plt.show ()

    fig.clf ()
    plt.close (fig)
    gc.collect ()

def hview (*imgs, saveas = None, titles = None, axis = True, dpi = 100, brg = True):
    if len (imgs) == 1 and isinstance (imgs [0], list):
        cols = len (imgs [0])
    else:
        cols = len (imgs)
    gview (cols, *imgs, saveas = saveas, titles = titles, axis = axis, dpi = dpi, brg = brg)

def vview (*imgs, saveas = None, titles = None, axis = True, dpi = 100, brg = True):
    gview (1, *imgs, saveas = saveas, titles = titles, axis = axis, dpi = dpi, brg = brg)
