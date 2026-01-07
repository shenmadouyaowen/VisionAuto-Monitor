from ultralytics import YOLO
import cv2
import numpy as np
import os

class YOLO11Detector:
    def __init__(self, model_path='models/best.pt'):
        self.model = YOLO(model_path)
        
    def detect(self, img, conf=0.5):
        """
        img: numpy array (BGR)
        Returns: list of detections [{'box': [x1, y1, x2, y2], 'conf': c, 'class': cls}]
        """
        results = self.model(img, conf=conf, verbose=False)
        detections = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                c = box.conf[0].item()
                cls = int(box.cls[0].item())
                detections.append({
                    'box': [x1, y1, x2, y2],
                    'conf': c,
                    'class': cls
                })
        return detections

    def get_center(self, box):
        x1, y1, x2, y2 = box
        return (x1 + x2) / 2, (y1 + y2) / 2
