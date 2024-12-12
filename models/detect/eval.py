from ultralytics import YOLO
import cv2

if __name__ == "__main__":
    
    model = YOLO("best.pt")
    
    frame = cv2.imread("hapa.jpg")
    # crop out 10% of the border    
    height, width, _ = frame.shape
    frame = frame[int(height * 0.1):int(height * 0.9), int(width * 0.1):int(width * 0.9)]
    
    predictions = model.predict(frame)
    
    # visualize
    for pred in predictions:
        pred.show()