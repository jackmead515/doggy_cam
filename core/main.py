import cv2
import numba as nb
import numpy as np

@nb.jit(nopython=True, fastmath=True)
def polar(x, y) -> tuple:
    return np.hypot(x, y), np.degrees(np.arctan2(y, x))


@nb.jit(nopython=True, fastmath=True)
def motion_detected(motion, window_size, threshold):
    l = int(np.ceil(motion.shape[0] / window_size) * np.ceil(motion.shape[1] / window_size))

    for i in nb.prange(l):
        x = (i % (motion.shape[1] / window_size)) * window_size
        y = (i // (motion.shape[1] / window_size)) * window_size
        window = motion[y:y+window_size, x:x+window_size]
        total_motion = np.count_nonzero(window) / (window_size**2)
        if total_motion > threshold:
            return True


# compile numba functions
motion_detected(np.zeros((640, 480), np.uint8), 64, 0.05)
polar(1, 1)


if __name__ == "__main__":
    
    #################################################################
    # INPUT VARIABLES
    input_pipe = 0
    width = 640
    height = 480
    fps = 30
    guassian_blur = 3
    median_blur = 5
    motion_window = 64
    min_motion_threshold = 100
    total_motion_threshold = 0.05
    total_motion_pixels = width * height
    skip_first = True
    #################################################################
    
    input = cv2.VideoCapture(input_pipe)
    input.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    input.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    input.set(cv2.CAP_PROP_FPS, fps)
    
    if not input.isOpened():
        print("Error: Could not open input")
        exit(1)
        
    prev = np.zeros((height, width, 3), np.uint8)
    current = np.zeros((height, width, 3), np.uint8)
    result = np.zeros((height, width), np.uint8)

    cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
    
    while True:

        success, _ = input.read(current)
        
        if not success:
            break
        
        if skip_first:
            np.copyto(prev, current)       
            skip_first = False
            continue
        
        prevg = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
        currentg = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)
        prevg = cv2.GaussianBlur(prevg, dst=None, ksize=(guassian_blur,guassian_blur), sigmaX=5)
        currentg = cv2.GaussianBlur(currentg, dst=None, ksize=(guassian_blur,guassian_blur), sigmaX=5)
        
        cv2.absdiff(prevg, currentg, result)
        
        result = cv2.normalize(result, None, 0, 255, cv2.NORM_MINMAX)
        result = cv2.medianBlur(result, median_blur)
        
        result[result < min_motion_threshold] = 0
        
        # raster scan with window
        if motion_detected(result, motion_window, total_motion_threshold):
            print("Motion detected")
            
        #flow = cv2.calcOpticalFlowFarneback(prevg, currentg, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        #magnitude, angle = polar(flow[..., 0], flow[..., 1])
        #result[..., 0] = angle*180/np.pi/2
        #result[..., 1] = 255
        #result[..., 2] = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)
        #result = cv2.cvtColor(result, cv2.COLOR_HSV2BGR)
        
        cv2.imshow('frame', current)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        np.copyto(prev, current)
    
    cv2.destroyAllWindows()
    input.release()
    
    print("Done")