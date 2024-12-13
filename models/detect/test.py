import numpy as np
import torch
from ultralytics import YOLO


if __name__ == "__main__":
    seed = 8149385
    
    np.random.seed(seed)
    torch.manual_seed(seed)
    
    model = YOLO("hapa.pt")
    
    # run on test images
    # model.val(
    #     data="dataset.yaml",
    #     imgsz=640,
    #     iou=0.7,
    #     seed=seed,
    #     amp=True,
    #     half=True,
    #     task="test",
    #     split="test",
    #     save_json=True
    # )
    
    model.export(format='onnx', opset=12, nms=True)