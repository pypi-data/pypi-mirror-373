import os
import json
import requests
import glob
import cv2
import io
import time
import logging
import numpy as np
from .utils.dataclass import DataClass, UnknownOption
from .utils.decorators import ensure_retry
from .utils import image_format
from .utils import config
from .prediction import BasePrediction

class TaskConfigurationError (Exception):
  pass

class HttpResponseError (Exception):
  pass

class BaseAnalyzer:
  TASK_TYPE = None
  PREDICTION_CLASS = BasePrediction
  PREDICTION_RETRY = 3
  MAX_IMAGE_LENGTH = 0

  def __init__ (self, backend = None, access_key = None):
    assert self.TASK_TYPE is not None
    self.config = config.get_config (backend, access_key)
    self.backend = self.config.server.backend
    self.access_key = self.config.server.access_key
    self.backend_version = None
    self._session = None
    self.fetch_options ()
    self.cleanup_temp_dir ()

  def _check_response (self, r, *args, **kwargs):
    if not (200 <= r.status_code < 300):
      try:
        err = r.json ()
      except:
        raise HttpResponseError (f'{r.status_code} {r.reason}, {r.text}')
      else:
        raise HttpResponseError (f'{r.status_code} {r.reason}, code:{err ["code"]} message:{err ["message"]}')

  @property
  def session (self):
    if self._session is None:
      self._session = requests.Session ()
      adapter = requests.adapters.HTTPAdapter (pool_connections = 10, pool_maxsize = 64)
      self._session.mount ('http://', adapter)
      self._session.mount ('https://', adapter)
      self._session.headers = {'Authorization': f'Bearer {self.access_key}'}
      self._session.hooks ['response'].append (self._check_response)
    return self._session

  def calibrate_options (self, data):
    for op in data ['options']:
      if op ['key'] == 'road_length_m':
        del op ['default']

  def before_reuqest (self, thresholds, options):
    return thresholds, options

  def after_reuqest (self, response):
    return response

  LOCAL_TEMP_DIR = '/tmp/kracknet/s3'
  def cleanup_temp_dir (self):
    an_hour_before = time.time () - 3600
    for it in glob.glob (os.path.join (self.LOCAL_TEMP_DIR, '*.*')):
      if os.path.getctime (it) < an_hour_before:
        try:
          os.remove (it)
        except (OSError, IOError):
          pass

  def ensure_image (self, img_path):
    img_name = os.path.basename (img_path)

    if img_path.startswith ('s3://'):
      from rs4.apis.aws import s3
      os.makedirs (self.LOCAL_TEMP_DIR, exist_ok = True)
      local_path = os.path.join (self.LOCAL_TEMP_DIR, os.path.basename (img_path))
      s3.download (img_path, local_path)
      assert os.path.isfile (local_path)
      img_path = local_path

    img_path = image_format.ensure_readable_image (img_path, self.LOCAL_TEMP_DIR)
    assert os.path.isfile (img_path), f'image not found: {img_path}'
    return img_path, img_name

  def predict (self, img_path) -> BasePrediction:
    img_path, img_name = self.ensure_image (img_path)
    if not self.MAX_IMAGE_LENGTH or self.options.output_image:
      prediction = self._predict (img_path, img_name)
    else:
      im, recov_factors = BaseAnalyzer.ensure_image_size (img_path, self.MAX_IMAGE_LENGTH)
      prediction = self._predict (img_path, img_name, im)
      if recov_factors:
        BaseAnalyzer.recover_image_size (prediction, recov_factors)
    return prediction

  @ensure_retry (PREDICTION_RETRY)
  def _predict (self, img_path, img_name = None, img_bytes = None):
    self.options.validate ()
    thresholds = self.thresholds.get_value ()
    options = self.options.get_value ()
    thresholds, options = self.before_reuqest (thresholds, options)

    data = {
      'threshold': json.dumps (thresholds),
      'options': json.dumps (options),
      'image_name': img_name or os.path.basename (img_path),
    }
    files = {'image': BaseAnalyzer.image_to_bytes (img_bytes) if img_bytes is not None else open (img_path, 'rb')}

    if self.backend_version >= '2.2':
      r = self.session.post (
        f'{self.backend}/apis/tasks/type/{self.TASK_TYPE}', data = data, files = files
      )
    else:
      data ['task_type'] = self.TASK_TYPE
      r = self.session.post (
        f'{self.backend}/apis/tasks/cli/outputs', data = data, files = files
      )
    response = r.json ()
    response = self.after_reuqest (response)
    return self.PREDICTION_CLASS (img_path, response)

  def save_configuration (self, out_path):
    data = {
      'version': str (self.backend_version),
      'task_type': self.TASK_TYPE,
      'setting': {
        'options': self.options.asdict (ignore_unset = True),
        'thresholds': self.thresholds.asdict (ignore_unset = True)
      }
    }
    with open (out_path, 'w') as f:
      f.write (json.dumps (data, indent = 2))

  def load_configuration (self, json_path):
    if isinstance (json_path, dict):
      data = json_path
    else:
      with open (json_path) as f:
        data = json.loads (f.read ())

    if str (self.backend_version [0]) >= "3" and data.get ('version', '2.0') [0] <= '2':
      raise TaskConfigurationError (f'incompatible configuration version')

    if data ['task_type'] != self.TASK_TYPE:
      raise TaskConfigurationError (f'mismatched task type')
    data ['setting']['threshold'] = data ['setting'].pop ('thresholds')
    self.apply_configuration (data ['setting'])

  def load_configuration_from_task (self, task_id):
    r = self.session.get (f'{self.backend}/apis/settings/{task_id}')
    data = r.json ()
    if data ['task_type'] != self.TASK_TYPE:
      raise TaskConfigurationError (f'mismatched task type')
    conf = json.loads (data ['setting'])
    self.apply_configuration (conf)

  def apply_configuration (self, conf):
    for k, v in conf ['options'].items ():
      try:
        setattr (self.options, k, v)
      except UnknownOption:
        logging.warning (f'unknown setting `{k}` is ignored')

    try:
      disabled = conf ['threshold'].pop ('__disabled__')
    except KeyError:
      disabled = {}

    for k, v in conf ['threshold'].items ():
      if k in disabled or v == 100:
        v = -1
      try:
        setattr (self.thresholds, k, v)
      except UnknownOption:
        logging.warning (f'unknown setting `{k}` is ignored')

  def sync_thresholds (self, code):
    try:
      val = getattr (self.thresholds, code)
    except UnknownOption:
      pass
    else:
      setattr (self.thresholds, code [:3] + '2' + code [-2:], val)
      setattr (self.thresholds, code [:3] + '3' + code [-2:], val)

  def fetch_options (self):
    r = self.session.get (f'{self.backend}/apis/versions')
    data = r.json ()
    self.backend_version = data.get ('backend', data ['pwa'])

    r = self.session.get (f'{self.backend}/apis/codes', params = {'task_type': self.TASK_TYPE, 'exclude_hidden': 'no'})
    data = r.json ()
    self.calibrate_options (data)

    valid_options = []
    for op in data ['options']:
      if op.get ('deprecated') or op.get ('noneed'):
        continue
      if 'api_only_name' in op:
        op ['name'] = op.pop ('api_only_name')
      if 'name' not in op:
        continue
      if op.get ('type') == 'boolean':
        op ['type'] = 'bool'
      op ['settable'] = True
      valid_options.append (op)
    self.options = DataClass (valid_options)

    thresholds = []
    for op in data ['codes']:
      if op.get ('deprecated') or op.get ('noneed'):
        continue
      if not op ['enabled']:
        op ['default'] = -1
      thresholds.append ({
          'key': op ['code'], 'default': op ['default'], 'valid_range': [-1, 99],
          'settable': not op ['hidden'],
          'name': op ['full_name'], 'type': 'int', 'color': tuple ([int (op ['color'] [i: i +2], 16) for i in range (0, 6, 2)])
      })
    self.thresholds = DataClass (thresholds)
    self.PREDICTION_CLASS.set_code_infos (self.options, self.thresholds)

  def get_summary (self):
    raise NotImplementedError


  @staticmethod
  def recover_image_size (prediction, recov_factors):
    result = prediction.json ()
    w, h, scale = recov_factors
    result ['imageHeight'] = h
    result ['imageWidth'] = w
    for shape in result ['shapes']:
      shape ['points'] = (np.array (shape ['points']) * [scale, scale]).astype (int).tolist ()
      shape ['bbox'] = (np.array (shape ['bbox']) * scale).astype (int).tolist ()

  @staticmethod
  def ensure_image_size (img_path, max_length):
    im = cv2.imread (img_path) if isinstance (img_path, str) else img_path
    h, w = im.shape [:2]
    resize = None
    if h > max_length:
      resize = (int (max_length * w / h), max_length)
    if w > max_length:
      resize = (max_length, int (max_length * h / w))
    if resize:
      im = cv2.resize (im, resize, interpolation = cv2.INTER_LANCZOS4)
    return im, None if not resize else (w, h, w / im.shape [1])

  @staticmethod
  def image_to_bytes (im):
    success, encoded_image = cv2.imencode (".jpg", im)
    return io.BytesIO (encoded_image.tobytes())