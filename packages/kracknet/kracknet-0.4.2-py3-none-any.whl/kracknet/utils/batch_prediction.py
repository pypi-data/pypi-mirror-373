import time
import rs4
from rs4.logger import print_exception
from . import plot

class FailedPrediction:
  def __init__ (self, img_path):
    self.img_path = img_path
    self.failed = True


@print_exception
def plot_anon_result (idx, prediction):
  source = prediction.get_image ()
  blur = prediction.blur ()
  plot.hview (source, blur)

@print_exception
def plot_dashcam_result (idx, prediction):
  source = prediction.get_image ()
  plotted = prediction.plot ()
  bev = prediction.generate_bev (height = 600, plot = True, show_label = False)
  plot.hview (source, plotted, bev)

@print_exception
def plot_roadscan_result (idx, prediction):
  source = prediction.get_image ()
  plotted = prediction.plot ()
  plot.hview (source, plotted)

@print_exception
def predict_in_pool (dca, path, idx, callback):
  try:
    prediction = dca.predict (path)
  except:
    prediction = FailedPrediction (path)

  if callback:
    prediction._result = callback (idx, prediction)
  return prediction

def predict (dca, batch, threads, callback = None, pool_type = 'thread'):
  pool_class = rs4.tpool if pool_type in ('thread', 'T', 't') else rs4.ppool
  started = time.time ()
  with pool_class (threads) as pool:
    queue = batch [:]
    tbar = rs4.tqdm (total = len (batch), desc = 'Analyzing')
    while queue:
      fs = []
      while queue:
        path = queue.pop (0)
        fs.append (pool.submit (predict_in_pool, dca, path, tbar.n, callback))
        if len (fs) == 200:
          break

      for f in rs4.as_completed (fs):
        f.result ()
        tbar.update ()
    tbar.close ()

  finished = time.time () - started
  print (f'Analysis Speed: {len (batch) / finished:.1f} ips')
