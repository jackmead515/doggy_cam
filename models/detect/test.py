import numpy as np
import torch
from ultralytics import YOLO


if __name__ == "__main__":
    seed = 8149385
    
    np.random.seed(seed)
    torch.manual_seed(seed)
    
    model = YOLO("runs/detect/train3/weights/best.pt")
    
    # run on test images
    model.val(
        data="dataset.yaml",
        imgsz=640,
        iou=0.7,
        seed=seed,
        amp=True,
        half=True,
        task="test",
        split="test",
        save_json=True
    )