import modal
import os
from pathlib import Path

# 1. 定义镜像
image = (
    modal.Image.debian_slim()
    .apt_install("libgl1", "libglib2.0-0")
    .pip_install("ultralytics", "opencv-python-headless")
)

app = modal.App("yolo11-retry-trainer")
volume = modal.Volume.from_name("yolo-data", create_if_missing=True)

@app.function(image=image, gpu="A10G", volumes={"/data": volume}, timeout=3600)
def train_yolo_remote():
    from ultralytics import YOLO
    import shutil
    
    # 训练数据预计在 /data/dataset
    data_yaml_path = "/data/data.yaml"
    
    # 确保 data.yaml 中的路径指向云端位置
    # 本地 data.yaml 的 path 是 ../dataset，云端需调整
    with open(data_yaml_path, 'r') as f:
        content = f.read()
    
    # 修正云端路径为 /data/dataset
    new_content = content.replace("path: ../dataset", "path: /data/dataset")
    with open(data_yaml_path, 'w') as f:
        f.write(new_content)

    model = YOLO("yolo11n.pt")
    model.train(
        data=data_yaml_path,
        epochs=100,
        imgsz=640,
        project="/data/runs",
        name="retry_model",
        exist_ok=True
    )
    
    # 导出为 ONNX
    trained_model = YOLO("/data/runs/retry_model/weights/best.pt")
    trained_model.export(format="onnx")
    
    # 复制导出的 onnx 到 weights 目录方便下载
    onnx_src = "/data/runs/retry_model/weights/best.onnx"
    onnx_dst = "/data/runs/retry_model/weights/retry_model.onnx"
    if os.path.exists(onnx_src):
        shutil.copy(onnx_src, onnx_dst)

    # 提交更改
    volume.commit()
    print("训练完成，模型已存入云端 Volume: /data/runs/retry_model/weights/")

@app.local_entrypoint()
def main():
    import sys
    import subprocess
    
    # 1. 同步本地数据到云端 Volume
    print("正在同步本地数据集到 Modal Volume (清理旧数据并重传)...")
    
    # 使用 sys.executable -m modal 确保使用的是虚拟环境中的 modal
    python_cmd = sys.executable
    
    # 清理旧数据 (忽略错误)
    subprocess.run(f'"{python_cmd}" -m modal volume rm yolo-data /dataset -r', shell=True)
    subprocess.run(f'"{python_cmd}" -m modal volume rm yolo-data /data.yaml', shell=True)
    
    # 上传 dataset 目录到 /dataset
    subprocess.run(f'"{python_cmd}" -m modal volume put yolo-data dataset /dataset', shell=True, check=True)
    # 上传 data.yaml 到 /data.yaml
    subprocess.run(f'"{python_cmd}" -m modal volume put yolo-data data.yaml /data.yaml', shell=True, check=True)
    
    print("数据集同步完成。")

    # 2. 触发云端训练
    print("正在启动云端训练 (GPU: A10G)...")
    train_yolo_remote.remote()

    # 3. 下载训练好的权重
    print("训练结束，正在下载权重到本地 models/ 目录...")
    os.makedirs("models", exist_ok=True)
    
    # 使用 modal volume get 下载权重
    print("使用 modal volume get 下载权重...")
    subprocess.run(f'"{python_cmd}" -m modal volume get yolo-data /runs/retry_model/weights/best.pt models/best.pt', shell=True, check=True)
    subprocess.run(f'"{python_cmd}" -m modal volume get yolo-data /runs/retry_model/weights/last.pt models/last.pt', shell=True, check=True)
    subprocess.run(f'"{python_cmd}" -m modal volume get yolo-data /runs/retry_model/weights/retry_model.onnx models/retry_model.onnx', shell=True, check=True)

    print("任务全部完成！")
