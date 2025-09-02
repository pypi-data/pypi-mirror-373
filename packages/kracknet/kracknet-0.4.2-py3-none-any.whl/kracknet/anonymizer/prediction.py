import os
import json
import numpy as np
import cv2
from rs4.annotations import override
from ..prediction import BasePrediction
from ..utils import blur
from ..utils import image_format

class Prediction (BasePrediction):
  @override
  def get_summary (self) -> dict:
    summary = []
    for k, v in self.result ['summary'].items ():
      summary.append ({
        'type': k,
        'metric': 'Count',
        'unit': None,
        'value': v
      })
    return summary

  def mask (self) -> cv2.typing.MatLike:
    im = image_format.ensure_readable_image (self.img_path)
    return blur.create_mask (im, self)

  def blur (self, intensity = None) -> cv2.typing.MatLike:
    im = image_format.ensure_readable_image (self.img_path)
    return blur.blurring (im, self, intensity or self.options.blur_intensity)

  def mosaic (self) -> cv2.typing.MatLike:
    im = image_format.ensure_readable_image (self.img_path)
    return blur.pixelate (im, self, self.options.blur_intensity)
