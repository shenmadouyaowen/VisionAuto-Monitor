from ultralytics import YOLO
import os

def download_weights():
    model_name = 'yolo11n.pt'
    target_dir = os.path.join('VisionAuto-Monitor', 'models')
    os.makedirs(target_dir, exist_ok=True)
    
    print(f"Downloading {model_name}...")
    model = YOLO(model_name)
    
    # The weights are usually downloaded to the current directory or the ultralytics default dir.
    # We move it to the models/ directory.
    if os.path.exists(model_name):
        target_path = os.path.join(target_dir, model_name)
        if os.path.exists(target_path):
            os.remove(target_path)  # Remove existing to allow rename
        os.rename(model_name, target_path)
        print(f"Weights saved to {target_path}")
    else:
        # Check if it already exists in the target dir
        target_path = os.path.join(target_dir, model_name)
        if os.path.exists(target_path):
            print(f"Weights already exist at {target_path}")
        else:
            print(f"Weights might have been saved elsewhere by ultralytics.")

if __name__ == "__main__":
    download_weights()
