from ultralytics import YOLO
import os

def train_model(data_yaml='data.yaml', epochs=10, imgsz=640):
    # Load a pretrained YOLO11n model
    model = YOLO('VisionAuto-Monitor/models/yolo11n.pt')

    # Train the model
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=imgsz,
        plots=True
    )
    
    # Export the model to ONNX for potential performance boost
    model.export(format='onnx')
    
    print("Training complete. Model saved in runs/detect/train/weights/")

if __name__ == "__main__":
    train_model()
