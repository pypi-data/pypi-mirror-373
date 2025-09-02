from functools import wraps
from rs4 import logger
import time
import logging
import sys

def ensure_retry (retry):
  from ..analyzer import HttpResponseError

  def decorator(f):
    @wraps(f)
    def wrapper (analyzer, img_path, *args):
      logging.info (f'predict {img_path}')
      n = retry + 1
      while n:
        try:
          return f (analyzer, img_path, *args)
        except Exception as e:
          n -= 1
          if not n or (isinstance (e, HttpResponseError) and 400 <= int (e.args [0][:3]) < 500):
            logging.error (logger.traceback ())
            raise
          t, v, tb = sys.exc_info ()
          logging.warning (f'{t.__name__}, retrying...')
          time.sleep (1)
    return wrapper
  return decorator