import logging
import cv2
import os
import tempfile
import shutil
from rs4 import tqdm

class Prediction:
  def __init__ (self, predictions, src_path, fps, resolution):
    self.predictions = predictions
    self.src_path = src_path
    self.fps = fps
    self.resolution = resolution
    self.vidfn, self.outvid = None, None

  def __len__ (self):
    return len (self.predictions)

  def __iter__ (self):
    return self.predictions.__iter__ ()

  def __del__ (self):
    if os.path.isdir (self.src_path):
      shutil.rmtree (self.src_path)

  def collect_images (self, out_path):
    if os.path.isdir (out_path):
      raise FileExistsError (f'Directory exists: {out_path}')
    shutil.copytree (self.src_path, out_path)

  def add_frame (self, frame):
    if self.vidfn is None:
      self.vidfn = tempfile.mktemp ('.mp4')
      fourcc = cv2.VideoWriter_fourcc (*'mp4v')
      self.outvid = cv2.VideoWriter (self.vidfn, fourcc, self.fps, self.resolution)
    self.outvid.write (frame)

  def create_video (self, out_path):
    self.outvid.release ()
    shutil.move (self.vidfn, out_path)


class VideoProcessor:
  def __init__ (self, analyzer):
    self.analyzer = analyzer

  def add_predictor (self, predictor):
    self.predictors.append (predictor)

  def predict (self, vid_path, nth_frame = 1, start_frame = 0, end_frame = 0) -> Prediction:
    logging.info (f'predict {vid_path}')
    cap = cv2.VideoCapture (vid_path)
    orig_fps = cap.get (cv2.CAP_PROP_FPS)
    fps = orig_fps / nth_frame
    fps = min (fps, orig_fps)

    width = int (cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int (cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    tempdir = tempfile.mkdtemp ('kracknet')

    total_frames = end_frame or int (cap.get(cv2.CAP_PROP_FRAME_COUNT)/nth_frame)
    pbar = tqdm (desc = f'Frame({nth_frame}th multiple frame)', total = total_frames)
    current_frame = 0
    predictions = []
    while True:
      ret, frame = cap.read ()
      if not ret or (end_frame and current_frame > end_frame + start_frame):
        break
      current_frame += 1
      if nth_frame > 1 and current_frame % nth_frame != 0:
        continue
      if current_frame < start_frame:
        continue

      img_path = f'{tempdir}/{current_frame:08d}.jpg'
      cv2.imwrite (img_path, frame)
      pred = self.analyzer.predict (img_path)
      predictions.append (pred)
      pbar.update ()

    pbar.close ()
    cap.release ()
    return Prediction (predictions, tempdir, fps, (width, height))
