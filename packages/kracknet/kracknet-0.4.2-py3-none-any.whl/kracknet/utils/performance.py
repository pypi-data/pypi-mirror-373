import numpy as np

def compute_iou_bb (boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
    boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
    boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)

    iou = interArea / float(boxAArea + boxBArea - interArea)
    return iou

def compute_iou (box1, boxes):
    x1 = np.maximum(box1[0], boxes[:, 0])
    y1 = np.maximum(box1[1], boxes[:, 1])
    x2 = np.minimum(box1[2], boxes[:, 2])
    y2 = np.minimum(box1[3], boxes[:, 3])

    inter_area = np.maximum(0, x2 - x1) * np.maximum(0, y2 - y1)

    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    boxes_area = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])

    union_area = box1_area + boxes_area - inter_area
    return inter_area / union_area

def compute_diou (box1, box2):
    iou = compute_iou(box1, box2.reshape(1, -1))[0]

    # Center distance
    center_box1 = [(box1[0] + box1[2]) / 2, (box1[1] + box1[3]) / 2]
    center_box2 = [(box2[0] + box2[2]) / 2, (box2[1] + box2[3]) / 2]
    center_dist = (center_box1[0] - center_box2[0]) ** 2 + (center_box1[1] - center_box2[1]) ** 2

    # Enclosing box
    enclosing_x1 = min(box1[0], box2[0])
    enclosing_y1 = min(box1[1], box2[1])
    enclosing_x2 = max(box1[2], box2[2])
    enclosing_y2 = max(box1[3], box2[3])
    enclosing_diag = (enclosing_x2 - enclosing_x1) ** 2 + (enclosing_y2 - enclosing_y1) ** 2

    return iou - center_dist / enclosing_diag






def nms (boxes, scores, iou_threshold=0.5):
  boxes = boxes.astype(np.float32)
  x1, y1, x2, y2 = boxes[:,0], boxes[:,1], boxes[:,2], boxes[:,3]
  areas = (x2 - x1 + 1) * (y2 - y1 + 1)
  order = scores.argsort()[::-1]
  keep = []
  while order.size > 0:
    i = order[0]
    keep.append(i)

    xx1 = np.maximum(x1[i], x1[order[1:]])
    yy1 = np.maximum(y1[i], y1[order[1:]])
    xx2 = np.minimum(x2[i], x2[order[1:]])
    yy2 = np.minimum(y2[i], y2[order[1:]])

    w = np.maximum(0.0, xx2 - xx1 + 1)
    h = np.maximum(0.0, yy2 - yy1 + 1)
    inter = w * h
    iou = inter / (areas[i] + areas[order[1:]] - inter)

    inds = np.where(iou <= iou_threshold)[0]
    order = order[inds + 1]

  return np.array(keep)

def soft_nms (boxes, scores, iou_threshold=0.5, sigma=0.5, score_threshold=0.001):
    boxes = boxes.copy()
    scores = scores.copy()
    indices = np.arange(len(boxes))
    picked_indices = []

    while len(scores) > 0:
        max_idx = np.argmax(scores)
        best_box = boxes[max_idx]
        best_score = scores[max_idx]
        best_index = indices[max_idx]
        picked_indices.append(best_index)

        boxes = np.delete(boxes, max_idx, axis=0)
        scores = np.delete(scores, max_idx)
        indices = np.delete(indices, max_idx)

        if len(boxes) == 0:
            break

        ious = compute_iou(best_box, boxes)
        scores = scores * np.exp(- (ious ** 2) / sigma)

        keep = scores > score_threshold
        boxes = boxes[keep]
        scores = scores[keep]
        indices = indices[keep]

    return np.array(picked_indices)

def diou_nms (boxes, scores, iou_threshold=0.5):
    idxs = scores.argsort()[::-1]
    picked_indices = []

    while len(idxs) > 0:
        current = idxs[0]
        picked_indices.append(current)
        idxs = idxs[1:]
        new_idxs = []
        for i in idxs:
            diou = compute_diou(boxes[current], boxes[i])
            if diou < iou_threshold:
                new_idxs.append(i)
        idxs = np.array(new_idxs)

    return np.array(picked_indices)






class F1ScoreBulder:
  def __init__ (self):
    self.data = []

  def add (self, preds, gt):
    self.data.append ((preds, gt))

  def compute_f1 (self, preds, gt, iou_threshold = 0.5, class_threshold = 0.25, duplicated = 'IGNORE'):
    if not len (gt) and not len (preds):
      return {'tp': 0, 'fp': 0, 'fn': 0, 'precision': 1.0, 'recall': 1.0, 'f1': 1.0}

    matched_gt = set ()
    tp, fp = 0, 0

    for pred in preds:
      pred_box = pred[:4]
      pred_label = pred[4]

      if pred [5] < (class_threshold [pred_label] if isinstance (class_threshold, dict) else class_threshold):
        continue

      matched = False
      for idx, gt_box in enumerate (gt):
        gt_box, gt_label = gt_box [:4], gt_box [4]
        if pred_label != gt_label:
          continue
        if compute_iou_bb (pred_box, gt_box) > iou_threshold:
          if idx in matched_gt:
            if duplicated == 'FP':
              matched = False
              break
          else:
            tp += 1
            matched_gt.add (idx)
          matched = True

      if not matched:
        fp += 1

    fn = len (gt) - len (matched_gt)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1        = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    return {'tp': tp, 'fp': fp, 'fn': fn, 'precision': precision, 'recall': recall, 'f1': f1}

  def global_f1 (self, data, iou_threshold):
    class F1Result:
      def __init__ (self, result):
        self.result = result
        self.precision = self.result ['images']['precision']
        self.recall = self.result ['images']['recall']
        self.f1 = self.result ['images']['f1']

      def __getitem__ (self, k):
        return self.result [k]

    tp, fp, fn = 0, 0, 0
    precisions, recalls, f1s = [], [], []
    for it in data:
      tp += it ['tp']
      fp += it ['fp']
      fn += it ['fn']
      precisions.append (it ['precision'])
      recalls.append (it ['recall'])
      f1s.append (it ['f1'])

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1        = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    return F1Result({
      'tp': tp, 'fp': fp, 'fn': fn, 'precision': precision, 'recall': recall, 'f1': f1,
      'images': {'precision': precisions, 'recall': recalls, 'f1': f1s}
    })

  def value (self, iou_threshold = 0.5, class_threshold = 0.25, duplicated = 'IGNORE'):
    data = []
    for preds, gt in self.data:
      data.append (self.compute_f1 (preds, gt, iou_threshold, class_threshold, duplicated))
    return self.global_f1 (data, iou_threshold)





def calculate_F1 (gt_labels, pred_labels):
  metric_fn = F1ScoreBulder ()
  for preds, gts in zip (pred_labels, gt_labels):
    preds, gts = np.array (preds), np.array (gts)
    metric_fn.add (preds, gts)
  return metric_fn
calculate_f1 = calculate_F1

def calculate_mAP (gt_labels, pred_labels, num_classes = 1):
  from mean_average_precision import MetricBuilder

  metric_fn = MetricBuilder.build_evaluation_metric ("map_2d", num_classes = num_classes)
  for preds, gts in zip (pred_labels, gt_labels):
    preds, gts = np.array (preds), np.array (gts)
    metric_fn.add (preds, gts)
  return metric_fn
