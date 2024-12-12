import cv2
import numba as nb
import numpy as np

@nb.jit(nopython=True, fastmath=True)
def polar(x, y) -> tuple:
    return np.hypot(x, y), np.degrees(np.arctan2(y, x))


@nb.jit(nopython=True, fastmath=True, parallel=True)
def motion_detected(motion, window_size, threshold):
    l = int(np.ceil(motion.shape[0] / window_size) * np.ceil(motion.shape[1] / window_size))
    detected = np.zeros(l, np.uint8)

    for i in nb.prange(l):
        x = (i % (motion.shape[1] / window_size)) * window_size
        y = (i // (motion.shape[1] / window_size)) * window_size
        window = motion[y:y+window_size, x:x+window_size]
        total_motion = np.count_nonzero(window) / (window_size**2)
        if total_motion > threshold:
            detected[i] = 1
    
    return detected


def detect_motion(prev, current, motion, guassian_blur=3, median_blur=5, min_motion_threshold=100, motion_window=64, total_motion_threshold=0.05):
    prevg = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
    currentg = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)
    prevg = cv2.GaussianBlur(prevg, dst=None, ksize=(guassian_blur, guassian_blur), sigmaX=5)
    currentg = cv2.GaussianBlur(currentg, dst=None, ksize=(guassian_blur, guassian_blur), sigmaX=5)
    
    cv2.absdiff(prevg, currentg, motion)
    
    motion = cv2.normalize(motion, None, 0, 255, cv2.NORM_MINMAX)
    motion = cv2.medianBlur(motion, median_blur)
    
    motion[motion < min_motion_threshold] = 0
    
    return motion_detected(motion, motion_window, total_motion_threshold)


def detect_objects(model, current, detect_conf_threshold=0.5):
    predictions = model.predict(current, verbose=False)
                
    for pred in predictions:
        
        boxes = pred.boxes.xyxy
        confs = pred.boxes.conf
        
        for i, box in enumerate(boxes):
            if confs[i] < detect_conf_threshold:
                continue
            
            x1, y1, x2, y2 = [int(i) for i in box]
            
            return x1, y1, x2, y2
        
        
def compile():
    motion_detected(np.zeros((640, 480), np.uint8), 64, 0.05)
    polar(1, 1)