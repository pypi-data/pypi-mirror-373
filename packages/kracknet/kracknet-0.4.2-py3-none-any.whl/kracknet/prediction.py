import os
import json
import cv2
import numpy as np
from .utils import image_format
from .utils import performance
import base64

def imdecode (b64_img):
  img_bytes = base64.b64decode (b64_img)
  nparr = np.frombuffer (img_bytes, np.uint8)
  return cv2.imdecode (nparr, cv2.IMREAD_COLOR)

class BasePrediction:
  @classmethod
  def set_code_infos (cls, options, thresholds):
    cls.options = options
    cls.thresholds = thresholds

  def __init__ (self, img_path, response):
    self.img_path = img_path
    if isinstance (response, str):
      with open (response) as f:
        self.response = {'result': f.read (), 'credit_balance': None}
    else:
      self.response = response
    self.result = json.loads (self.response.pop ('result'))

  def __getitem__ (self, k, v = None):
    return self.result.get (k, v)

  def __setitem__ (self, k, v):
    return self.result.set (k, v)

  def __delitem__ (self, k):
    return self.result.pop (k)

  def __len__ (self):
    return len (self.result ['shapes'])

  def __iter__ (self):
    for it in self.result ['shapes']:
      yield it

  def nms (self, iou_threshold = 0.5, method = 'diou_nms') -> None:
    assert method in ('nms', 'diou_nms', 'soft_nms')
    labels = set ()
    for it in self.result ['shapes']:
      assert 'bbox' in it, 'nms need bbox informatoin'
      labels.add (it ['label'])

    nresults = []
    for label in labels:
      per_label_results = []
      bboxes, scores = [], []
      for it in self.result ['shapes']:
        if it ['label'] != label:
          continue
        bboxes.append (it ['bbox'])
        scores.append (it ['score'])
        per_label_results.append (it)

      nms_iou_threshold = iou_threshold [label] if isinstance (iou_threshold, dict) else iou_threshold
      meth = getattr (performance, method)
      indices = meth (np.array (bboxes), np.array (scores), nms_iou_threshold)
      nresults.extend ([r for idx, r in enumerate (per_label_results) if idx in indices])
    self.result ['shapes'] = nresults

  def save_json (self, path):
    r = self.json ()
    with open (path, 'w') as f:
      f.write (json.dumps (r, indent = 2))

  def json (self) -> dict:
    return self.result

  def get_credit_balance (self) -> int:
    return self.response ['credit_balance']

  def get_image (self) -> cv2.typing.MatLike:
    return image_format.ensure_readable_image (self.img_path)

  def get_output_image (self) -> cv2.typing.MatLike:
    assert 'output_image' in self.response, 'options.output_image shoud be true'
    return imdecode (self.response ['output_image'])

  def plot (self, show_label = True) -> cv2.typing.MatLike:
    im = image_format.ensure_readable_image (self.img_path)
    for it in self:
      self.draw (im, it, show_label = show_label)
    return im

  def draw (self, im, d, show_label = True):
    points = np.reshape (d ['points'], (-1, 2)).astype (int)
    label = '{} {:.2f}'.format (d ["label"], d ['score'])
    line_color = self.thresholds.get_spec (d ["label"]) ['color']
    shape = d ['shape_type']
    current_line_width = 2
    if "severity" in d:
      current_line_width = {'Severe': 7, 'Moderate': 4, 'Minor': 1, 'Critical': 7, 'Major': 4} [d ["severity"]]
    zoom_factor = (im.shape [0] / 1080)
    current_line_width = int (current_line_width * zoom_factor)

    if shape == 'rectangle':
      cv2.rectangle (im, points [0], points [1], line_color, current_line_width)
      text_pos = [points [0][0], points [0][1] - 10]
    elif shape in ('linestrip', 'polygon'):
      cv2.polylines (im, np.array ([points]), True if shape == 'polygon' else False, line_color, current_line_width, cv2.LINE_AA)
      if shape == 'linestrip':
        text_pos = [points [0][0], points [0][1] - 10]
      else:
        x1, y1 = np.min (points, 0).tolist ()
        text_pos = [x1, y1 - 10]
    elif shape == 'ellipse':
      cv2.ellipse (im, points [0], points [1], 0, 0, 360, line_color, current_line_width, lineType = cv2.LINE_AA)
      x1, y1 = [points [0][0] - points [1][0], points [0][1] - points [1][1]]
      text_pos = [x1, y1 - 10]
    else:
      raise ValueError (f'Unknown shape {d ["shape_type"]}')

    if show_label:
      cv2.rectangle (im, (text_pos [0] - int (1 * zoom_factor), text_pos [1] - int (9 * zoom_factor)), (text_pos [0] + int (80 * zoom_factor), text_pos [1] + int (5 * zoom_factor)), 64, -1)
      cv2.rectangle (im, (text_pos [0] - int (4 * zoom_factor), text_pos [1] - int (12 * zoom_factor)), (text_pos [0] + int (80 * zoom_factor), text_pos [1] + int (5 * zoom_factor)), line_color, -1)
      cv2.putText (im, label, text_pos, cv2.FONT_HERSHEY_PLAIN, 0.7 * zoom_factor, (255, 255, 255), int (1 * zoom_factor), cv2.LINE_AA)
