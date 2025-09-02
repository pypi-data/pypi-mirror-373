#! /usr/bin/env python3

import click
import os
import logging
import rs4
import toml
import cv2
import glob
import sys

# commands --------------------------------------------------
@click.group()
@click.option('-d', '--debug', is_flag=True, default = False)
@click.pass_context
def cli (context, debug):
  debug and logging.basicConfig (level = logging.DEBUG)

@cli.command ()
@click.option ('--access-key', prompt = True, required = True)
@click.option ('--backend', prompt = True, default = 'https://kracknet.com')
@click.pass_context
def configure (context, access_key, backend):
  """Configuring backend URL and API access key"""
  assert backend.startswith ('http'), 'backend should be start with http:// or https://'
  os.makedirs (os.path.expanduser ('~/.kracknet'), exist_ok = True)
  with open (os.path.expanduser ('~/.kracknet/config'), 'w') as f:
    toml.dump ({'server': {'access_key': access_key, 'backend': backend}}, f)

def handle_output (pred, output, fn, json, plot_image = False, bev_image = False, blurred_image = False, bev_plot = False):
  if json:
    path = os.path.join (output, f'{fn}.json')
    pred.save_json (path)
    logging.info (f'JSON saved as {path}')

  if blurred_image:
    im = pred.blur ()
    path = os.path.join (output, f'{fn}.blurred.jpg')
    cv2.imwrite (path, im)
    logging.info (f'blurred image saved as {path}')

  if plot_image:
    im = pred.plot ()
    path = os.path.join (output, f'{fn}.plot.jpg')
    cv2.imwrite (path, im)
    logging.info (f'plot image saved as {path}')

  if bev_image:
    im = pred.generate_bev (1080, plot = bev_plot)
    path = os.path.join (output, f'{fn}.bev.jpg')
    cv2.imwrite (path, im)
    logging.info (f'BEV image saved as {path}')

def create_analyzer (predictor_class, source, output, load_config_from_task, load_config, save_config):
  if len (source) == 1:
    if not source [0].startswith ('s3://'):
      assert os.path.isfile (source [0]) or glob.glob (source [0]), "input not found"
  assert os.path.isdir (output), "output should be an directory"

  an = predictor_class ()
  if load_config_from_task:
    an.load_configuration_from_task (load_config_from_task)
    logging.info (f'load configuration from task {load_config_from_task}')
  if load_config:
    an.load_configuration (load_config)
    logging.info (f'load configuration from file {load_config}')
  if save_config:
    an.save_configuration (save_config)
    logging.info (f'configuration saved as {save_config}')
  return an

def predict (an, source, output, json, plot_image = False, bev_image = False, blurred_image = False, bev_plot = False, nth_frame = 30):
  from .utils.video_processor import VideoProcessor

  _, base = os.path.split (source)
  fn, ext = os.path.splitext (base)
  if bev_plot:
    bev_image = True

  is_video = ext.lower () in ('.mp4', '.mov', '.avi', '.mkv', '.ts', '.webm', '.flv', 'mpeg', '.mpg')

  if not is_video:
    pred = an.predict (source)
    handle_output (pred, output, fn, json, plot_image, bev_image, blurred_image, bev_plot)
    return

  vp = VideoProcessor (an)
  pred = vp.predict (source, nth_frame = nth_frame)
  for p in rs4.tqdm (pred, total = len (pred), desc = 'Creating frames'):
    if int (plot_image) + int (bev_image) + int (blurred_image) != 1:
      raise RuntimeError ('specify only one of --plot-image, --bev-image or --blurred-image to create video')
    pred.add_frame (p.blur () if hasattr (p, 'get_blurred_image') else p.plot (show_label = False))
    handle_output (p, output, fn, json, plot_image, bev_image, blurred_image, bev_plot)

  path = os.path.join (output, f'{fn}.mp4')
  pred.create_video (path)
  logging.info (f'Video saved as {path}')

def process (concurrent, an, source, *args, **kwargs):
  q = []
  for it in source:
    if it.startswith ('s3://'):
      q.append (it)
    elif os.path.isdir (it):
      q.extend (glob.glob (os.path.join (it, '*.*')))
    else:
      q.extend (glob.glob (it))

  if len (q) == 0:
    raise RuntimeError ('no input files or directory')

  if len (q) == 1:
    return predict (an, q [0], *args, **kwargs)

  with rs4.ppool (concurrent) as pool:
    fs = []
    for source in rs4.tqdm (q, desc = 'Queueing'):
      fs.append (pool.submit (predict, an, source, *args, **kwargs))
    for f in rs4.tqdm (rs4.as_completed (fs), desc = 'Processing', total = len (fs)):
      pass

@cli.command ()
@click.argument ('source')
@click.option ('-o', '--output', default = './', help = 'folder to save frame')
@click.option ('-f', '--nth-frame', default = 30, help = 'handle the nth multiple frame only')
@click.option ('-s', '--start-frame', default = 0, help = 'start frame number')
@click.option ('-e', '--end-frame', default = 0, help = 'start frame number')
@click.pass_context
def frame (context, source, output, nth_frame, start_frame, end_frame):
  """Extract frames from video"""
  from .utils.video_processor import VideoProcessor

  class DummyAnlayzer:
    def predict (self, img_path):
      return

  if os.path.isdir (output):
      raise FileExistsError (f'Directory exists: {output}')
  an = VideoProcessor (DummyAnlayzer ())
  pred = an.predict (source, nth_frame, start_frame, end_frame)
  pred.collect_images (output)
  logging.info (f'Frames saved as {output}')

def common_options (function):
  function = click.argument ('source', nargs = -1) (function)
  function = click.option ('-o', '--output', default = './', help = 'folder to save result') (function)
  function = click.option ('-t', '--load-config-from-task', default = None, type = int, help = 'existing task ID to apply task configuration') (function)
  function = click.option ('-c', '--concurrent', default = 1, help = 'concurrent ') (function)
  function = click.option ('-f', '--nth-frame', default = 30, help = 'handle the nth multiple frame only (if source is video)') (function)
  function = click.option ('-j', '--json', is_flag = True, default = False, help = 'save result as json (*.json)') (function)
  function = click.option ('-p', '--plot-image', is_flag = True, default = False, help = 'save result as plot image (*.plot.jpg)') (function)
  function = click.option ('--load-config', default = None, help = 'load JSON task configuration') (function)
  function = click.option ('--save-config', default = None, help = 'save task configuration as JSON') (function)
  return function

@cli.command ()
@common_options
@click.option ('-b', '--blurred-image', is_flag = True, default = False, help = 'save result as blurred image (*.blurred.jpg)')
@click.pass_context
def anon (context, source, output, json, plot_image, blurred_image, load_config_from_task, load_config, concurrent, nth_frame, save_config):
  """Anonymize SOURCE image/video or folder which contains them"""
  from .anonymizer import ImageAnonymizer
  an = create_analyzer (ImageAnonymizer, source, output, load_config_from_task, load_config, save_config)
  process (concurrent, an, source, output, json, plot_image = plot_image, blurred_image = blurred_image, nth_frame = nth_frame)

@cli.command ()
@common_options
@click.option ('-b', '--bev-image', is_flag = True, default = False, help = 'save result as bird\'s eye view image (*.bev.jpg)')
@click.option ('--bev-plot', is_flag = True, default = False, help = 'plot on bev image')
@click.pass_context
def dashcam (context, source, output, json, plot_image, bev_image, load_config_from_task, load_config, concurrent, nth_frame, save_config, bev_plot):
  """Analyze road pavement from dash cam image/video or folder which contains them"""
  from .road_analyzer import DashCamImageAnalyzer
  an = create_analyzer (DashCamImageAnalyzer, source, output, load_config_from_task, load_config, save_config)
  process (concurrent, an, source, output, json, bev_image = bev_image, plot_image = plot_image, nth_frame = nth_frame, bev_plot = bev_plot)

@cli.command ()
@common_options
@click.pass_context
def roadscan (context, source, output, json, plot_image, load_config_from_task, load_config, concurrent, nth_frame, save_config):
  """Analyze road pavement from flat road scan image/video or folder which contains them"""
  from .road_analyzer import RoadScanImageAnalyzer
  an = create_analyzer (RoadScanImageAnalyzer, source, output, load_config_from_task, load_config, save_config)
  process (concurrent, an, source, output, json, plot_image = plot_image, nth_frame = nth_frame)

def main ():
  cli (obj = {})

if __name__ == "__main__":
  main ()
