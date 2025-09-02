import os
import cv2
import numpy as np
from PIL import Image
import pillow_avif

def pil_to_cv2 (pil_image):
  cv2_image = np.array (pil_image)
  cv2_image = cv2.cvtColor (cv2_image, cv2.COLOR_RGB2BGR)
  return cv2_image

def read_avif (img_path):
  return pil_to_cv2 (Image.open (img_path))


def ensure_readable_image (img_path, temp_dir = None):
  im = None
  if img_path.lower ().endswith ('.avif'):
    im = read_avif (img_path)
    assert im is not None, f'converting image failed: {img_path}'
  elif temp_dir is None:
    im = cv2.imread (img_path)
    assert im is not None, f'reading image failed: {img_path}'

  if temp_dir:
    if im is None:
      return img_path
    os.makedirs (temp_dir, exist_ok = True)
    temp_fn = os.path.join (temp_dir, os.path.splitdrive (os.path.basename (img_path)) [0] + '.jpg')
    cv2.imwrite (temp_fn, im)
    assert os.path.isfile (temp_fn), f'writing image failed: {img_path}'
    return temp_fn

  return im
