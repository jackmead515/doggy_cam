from typing import Tuple

import cv2
import numba as nb
import numpy as np
import torchvision as tv
import torch as t

@nb.jit(nopython=True, fastmath=True)
def polar(x, y) -> tuple:
    return np.hypot(x, y), np.degrees(np.arctan2(y, x))


@nb.jit(nopython=True, fastmath=True, parallel=True)
def motion_detected(motion, window_size, threshold):
    """
    For each window of size window_size x window_size in the motion image, check
    if the total motion percentage is greather than the threshold. If it is, mark
    it as detected=1, otherwise detected=0
    """
    square = window_size**2
    l = int(np.ceil(motion.shape[0] / window_size) * np.ceil(motion.shape[1] / window_size))
    detected = np.zeros(l, np.uint8)
    
    for i in nb.prange(l):
        x = (i % (motion.shape[1] / window_size)) * window_size
        y = (i // (motion.shape[1] / window_size)) * window_size
        window = motion[y:y+window_size, x:x+window_size]
        total_motion = np.count_nonzero(window) / square
        if total_motion > threshold:
            detected[i] = 1
    
    return detected


@nb.jit(nopython=True, fastmath=True)
def to_tensor(np_image):
    """convert numpy image to tensor format using numpy"""
    return (np.expand_dims(np.transpose(np_image, (2, 0, 1)), axis=0) / 255.0).astype(np.float32)


def format_boxes(output, height, width, input_dim, detect_conf_threshold, nms_threshold=0.7):
    """
    Format the output of the YOLO model in onnx format to retrieve the bounding boxes and confidence scores
    applying non-maximum suppression to remove overlapping boxes
    """
    output = output[0][0].T

    scores = np.max(output[:, 4:], axis=1)
    output = output[scores > detect_conf_threshold, :]
    scores = scores[scores > detect_conf_threshold]
    
    if len(scores) == 0:
        return None
    
    boxes = output[:, :4]
    input_shape = np.array([input_dim, input_dim, input_dim, input_dim])
    boxes = np.divide(boxes, input_shape, dtype=np.float32)
    boxes *= np.array([width, height, width, height])
    
    indicies = tv.ops.nms(t.tensor(boxes), t.tensor(scores), nms_threshold)
    
    boxes = boxes[indicies].astype(np.int32)
    scores = scores[indicies]
    
    return boxes, scores


def detect_motion(prev, current, motion, guassian_blur=3, noise_threshold=100, motion_window=64, total_motion_threshold=0.05):
    """
    Calculate the motion between two frames using the absolute difference between the grayscale images
    and retrieve the windows where the total motion is greater than the threshold.
    """
    prevg = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
    currentg = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)
    cv2.GaussianBlur(prevg, dst=prevg, ksize=(guassian_blur, guassian_blur), sigmaX=guassian_blur)
    cv2.GaussianBlur(currentg, dst=currentg, ksize=(guassian_blur, guassian_blur), sigmaX=guassian_blur)
    cv2.absdiff(prevg, currentg, motion)
    
    motion[motion < noise_threshold] = 0
    motion[motion >= noise_threshold] = 255
    
    return motion_detected(motion, motion_window, total_motion_threshold)


def detect_objects(model, current, detect_conf_threshold=0.5, input_dim=640) -> Tuple[Tuple[int, int, int, int], float] | None:
    """
    Use the YOLO model to detect objects in the current frame and return the bounding boxes and confidence scores
    """

    height, width = current.shape[:2]

    current = cv2.cvtColor(current, cv2.COLOR_BGR2RGB)
    current = cv2.resize(current, (input_dim, input_dim))
    
    input = to_tensor(current)
    
    output = model.run(None, {'images': input})
    
    output = format_boxes(output, height, width, input_dim, detect_conf_threshold)
    
    if output is not None:
        box, conf = output
        return box, conf


def compile():
    motion_detected(np.zeros((640, 480), np.uint8), 64, 0.05)
    to_tensor(np.zeros((640, 480, 3), np.uint8))
    polar(1, 1)