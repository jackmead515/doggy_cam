import os
import multiprocessing

import numpy as np
import torch
from ultralytics import YOLO


if __name__ == "__main__":
    seed = 8149385
    
    np.random.seed(seed)
    torch.manual_seed(seed)
    
    model = YOLO("yolo11n.pt")
    
    # https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/default.yaml
    model.train(
        data="dataset.yaml",
        seed=seed,
        amp=True,
        half=True,
        epochs=100,
        imgsz=640,
        batch=-1,
        iou=0.7,
        max_det=10,
        degrees=15.0
    )