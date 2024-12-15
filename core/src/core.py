import time
import logging

import cv2
import numpy as np
import onnxruntime

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
    
    model = onnxruntime.InferenceSession(config.model_path)
    tracker = cv2.legacy.TrackerCSRT_create()

    prev = np.zeros((config.height, config.width, 3), np.uint8) # the previous frame
    current = np.zeros((config.height, config.width, 3), np.uint8) # the current frame
    motion = np.zeros((config.height, config.width), np.uint8) # the buffer for the motion detection
    motion_window = int(config.width * config.window_perc)
    skip_first = True
    use_tracker = False
    tracker_index = 0
    redetect_index = 0
    
    fps_buffer = np.zeros(30)
    start_time = time.perf_counter()
    fps_index = 0
    fps = 0

    #cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
    
    while True:

        success, _ = input.read(current)
        
        if not success:
            break
        
        # skip the first frame to make sure previous frame is not empty
        if skip_first:
            np.copyto(prev, current)
            skip_first = False
            logging.info(f'First frame captured. Size: {current.shape}')
            continue
        
        # utilizing the tracker to track the currently detected object
        if use_tracker:
            redetect_index = 0
            tracker_index += 1
            
            # if we have tracked the object for a number of frames,
            # re-detect the object to ensure we are still tracking the correct object
            # if we don't detect it, we will need to re-detect the object
            if tracker_index == config.tracker_frames:
                detected = util.detect_objects(model, current, detect_conf_threshold=config.detect_conf_threshold)

                if detected is not None:
                    box, conf = detected
                    x1, y1, x2, y2 = [int(v) for v in box]
                    x, y, w, h = x1, y1, x2-x1, y2-y1
                    
                    tracker = cv2.legacy.TrackerCSRT_create()
                    tracker.init(current, (x, y, w, h))
                    tracker_index = 0
                    use_tracker = True
                    
                    #cv2.rectangle(current, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    events.push('core.object.detected', {
                        'box': [x1, y1, x2, y2],
                        'confidence': float(conf),
                    })

                else:
                    use_tracker = False
            
            else:
                success, box = tracker.update(current)
                
                # we have successfully tracked the object, draw the box
                if success:
                    (x, y, w, h) = [int(v) for v in box]
                    x1, y1, x2, y2 = x, y, x+w, y+h
                    
                    #cv2.rectangle(current, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    events.push('core.object.tracked', {
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
            
            detected = util.detect_objects(model, current, detect_conf_threshold=config.detect_conf_threshold)

            if detected is not None:
                box, conf = detected
                x1, y1, x2, y2 = [int(v) for v in box]
                x, y, w, h = x1, y1, x2-x1, y2-y1
                
                tracker = cv2.legacy.TrackerCSRT_create()
                tracker.init(current, (x, y, w, h))
                tracker_index = 0
                use_tracker = True
                
                #cv2.rectangle(current, (x1, y1), (x2, y2), (0, 255, 0), 2)
                events.push('core.object.detected', {
                    'box': [x1, y1, x2, y2],
                    'confidence': float(conf),
                })

        # else increment the redetect index to attempt to re-detect the object
        else:
            redetect_index += 1


        detected = util.detect_motion(
            prev,
            current,
            motion,
            guassian_blur=config.guassian_blur,
            noise_threshold=config.noise_threshold,
            motion_window=motion_window,
            total_motion_threshold=config.total_motion_threshold
        )

        if np.sum(detected) > config.motion_detected_windows:
            events.push('core.motion.detected', {
                'detected': int(np.sum(detected)),
                'total': len(detected),
            })
            
            # for i in range(len(detected)):
            #     if detected[i] == 1:
            #         x = int((i % (motion.shape[1] / motion_window)) * motion_window)
            #         y = int((i // (motion.shape[1] / motion_window)) * motion_window)
            #         cv2.rectangle(current, (x, y), (x+motion_window, y+motion_window), (0, 255, 0), 2)


        # update the FPS for monitoring purposes
        fps_buffer[fps_index] = (time.perf_counter() - start_time)
        start_time = time.perf_counter()
        fps_index += 1
        if fps_index == len(fps_buffer):
            fps = len(fps_buffer) / np.sum(fps_buffer)
            fps_index = 0
            
            logging.info(f"FPS: {fps}")
            
        
        # cv2.imshow('frame', current)

        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break
        
        np.copyto(prev, current)

    #cv2.destroyAllWindows()
    input.release()