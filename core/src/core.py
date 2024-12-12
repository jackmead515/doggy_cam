import time
from datetime import datetime, timezone
import cv2
import numba as nb
import numpy as np
from ultralytics import YOLO

import config
import events
import util

def run():
    input = cv2.VideoCapture(config.input_pipe)
    input.set(cv2.CAP_PROP_FRAME_WIDTH, config.width)
    input.set(cv2.CAP_PROP_FRAME_HEIGHT, config.height)
    input.set(cv2.CAP_PROP_FPS, config.fps)
    
    if not input.isOpened():
        raise Exception("Could not open video source")
        
    model = YOLO(config.model_path, verbose=False, task="detect")
    tracker = cv2.legacy.TrackerCSRT_create()

    prev = np.zeros((config.height, config.width, 3), np.uint8) # the previous frame
    current = np.zeros((config.height, config.width, 3), np.uint8) # the current frame
    motion = np.zeros((config.height, config.width), np.uint8) # the buffer for the motion detection
    motion_window = int(config.width * config.window_perc)
    skip_first = True
    use_tracker = False
    start_recording = False
    tracker_index = 0
    redetect_index = 0
    
    detection_buffer = np.zeros(30)
    detection_index = 0
    
    fps_buffer = np.zeros(30)
    start_time = time.perf_counter()
    fps_index = 0
    fps = 0

    cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
    
    while True:

        success, _ = input.read(current)
        
        if not success:
            break
        
        # skip the first frame to make sure previous frame is not empty
        if skip_first:
            np.copyto(prev, current)
            skip_first = False
            continue
        
        # utilizing the tracker to track the currently detected object
        if use_tracker:
            redetect_index = 0
            tracker_index += 1
            
            # if we have tracked the object for a number of frames,
            # re-detect the object to ensure we are still tracking the correct object
            # if we don't detect it, revert to motion detection
            if tracker_index == config.tracker_frames:
                box = util.detect_objects(model, current, detect_conf_threshold=config.detect_conf_threshold)

                if box is not None:
                    x1, y1, x2, y2 = box
                    x, y, w, h = x1, y1, x2-x1, y2-y1
                    
                    tracker = cv2.legacy.TrackerCSRT_create()
                    tracker.init(current, (x, y, w, h))
                    tracker_index = 0
                    use_tracker = True
                    
                    cv2.rectangle(current, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    detection_buffer[detection_index] = 2
                    events.push('object.detected', {
                        'box': [x1, y1, x2, y2],
                    })

                else:
                    use_tracker = False
            
            else:
                success, box = tracker.update(current)
                
                # we have successfully tracked the object, draw the box
                if success:
                    (x, y, w, h) = [int(v) for v in box]
                    cv2.rectangle(current, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    detection_buffer[detection_index] = 1
                    events.push('object.tracked', {
                        'track_index': tracker_index,
                        'box': [x1, y1, x2, y2],
                    })

                # if the tracker failed, we need to re-detect the object
                # TODO: should add some logic to re-detect without motion detection
                else:
                    use_tracker = False

        # else if we have reached a point to attempt to re-detect the object
        # try and detect an object, if we find one, start tracking it
        elif redetect_index >= config.redetect_interval:
            redetect_index = 0
            
            box = util.detect_objects(model, current, detect_conf_threshold=config.detect_conf_threshold)
            if box is not None:
                x1, y1, x2, y2 = box
                x, y, w, h = x1, y1, x2-x1, y2-y1
                
                tracker = cv2.legacy.TrackerCSRT_create()
                tracker.init(current, (x, y, w, h))
                tracker_index = 0
                use_tracker = True
                
                cv2.rectangle(current, (x1, y1), (x2, y2), (0, 255, 0), 2)
                detection_buffer[detection_index] = 2
                events.push('object.detected', {
                    'box': [x1, y1, x2, y2],
                })

        # else revert to motion detection as the trigger for object detection
        else:
            redetect_index += 1
            detected = util.detect_motion(
                prev,
                current,
                motion,
                guassian_blur=config.guassian_blur,
                median_blur=config.median_blur,
                min_motion_threshold=config.min_motion_threshold,
                motion_window=motion_window,
                total_motion_threshold=config.total_motion_threshold
            )
            
            if np.sum(detected) > config.motion_detected_windows:
                detection_buffer[detection_index] = 1
                box = util.detect_objects(model, current, detect_conf_threshold=config.detect_conf_threshold)

                if box is not None:
                    x1, y1, x2, y2 = box
                    x, y, w, h = x1, y1, x2-x1, y2-y1
                    
                    tracker = cv2.legacy.TrackerCSRT_create()
                    tracker.init(current, (x, y, w, h))
                    tracker_index = 0
                    use_tracker = True
                    
                    cv2.rectangle(current, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    detection_buffer[detection_index] = 2
                    events.push('object.detected', {
                        'box': [x1, y1, x2, y2],
                    })
        
        # update the FPS for monitoring purposes
        fps_buffer[fps_index] = (time.perf_counter() - start_time)
        start_time = time.perf_counter()
        fps_index += 1
        if fps_index == len(fps_buffer):
            fps = len(fps_buffer) / np.sum(fps_buffer)
            fps_index = 0

        # update the detection buffer to trigger recording or not
        detection_index += 1
        if detection_index == len(detection_buffer):
            detection_index = 0
            summ = np.sum(detection_buffer)
            threshold = config.recorder_sensitivity * len(detection_buffer)
            
            if not start_recording and summ >= threshold:
                start_recording = True
                events.push('recording.started', {})

            elif start_recording and summ == 0:
                start_recording = False
                events.push('recording.stopped', {})
                
            detection_buffer = np.zeros(len(detection_buffer))

        cv2.putText(current, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(current, f"Recording: {start_recording}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        cv2.imshow('frame', current)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        np.copyto(prev, current)

    cv2.destroyAllWindows()
    input.release()