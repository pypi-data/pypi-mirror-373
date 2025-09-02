from rs4.annotations import override
from ..analyzer import BaseAnalyzer
from .prediction import Prediction

class ImageAnonymizer (BaseAnalyzer):
  TASK_TYPE = 5
  PREDICTION_CLASS = Prediction
  MAX_IMAGE_LENGTH = 2472

  @override
  def before_reuqest (self, thresholds, options):
    options ['object_boxing'] = False
    options ['blur_patch'] = False
    options ['overlay_boxing'] = False
    return thresholds, options

  @override
  def calibrate_options (self, data):
    super ().calibrate_options (data)
    for op in data ['options']:
      if op ['key'] in ('object_boxing',):
        del op ['name']

  @override
  def predict (self, img_path) -> Prediction:
    return super ().predict (img_path)
