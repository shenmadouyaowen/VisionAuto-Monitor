# VisionAuto-Monitor (YOLO11)

VisionAuto-Monitor 是一个全自动视觉监控与操作工具。它允许用户选择特定的屏幕区域，使用 YOLO11 进行目标检测（例如：重试按钮），并在检测到目标时自动执行鼠标点击操作。

## 项目结构

- `src/ui/`: 包含区域选择器 (`selector.py`) 和主控制面板 (`dashboard.py`)。
- `src/core/`: 核心逻辑组件：
  - `capturer.py`: 高性能屏幕截图。
  - `detector.py`: YOLO11 检测逻辑。
  - `executor.py`: 鼠标点击执行。
- `scripts/`: 工具脚本：
  - `data_synth.py`: 合成数据集生成器。
  - `train.py`: YOLO11 训练脚本。
  - `download_weights.py`: 权重下载脚本。
- `models/`: 存放训练好的模型文件 (`.pt`, `.onnx`)。
- `dataset/`: 存放生成的训练数据。

## 使用步骤

### 1. 准备训练数据
由于此类特定按钮的样本较少，我们需要生成合成数据：
1. 准备一张按钮的图标图片（例如 `retry_btn.png`）。
2. 准备一些背景截图（例如 IDE 的截图）。
3. 修改 `scripts/data_synth.py` 中的路径并运行，生成 500+ 张各种背景下的按钮图片。

```bash
# 修改路径后运行
python scripts/data_synth.py
```

### 2. 训练模型
运行训练脚本来微调 YOLO11n：

```bash
python scripts/train.py
```

### 3. 运行监控工具
训练完成后，启动主界面：

```bash
python -m src.ui.dashboard
```

### 4. 操作说明
1. 点击 **"Select Region"**，在屏幕上拖拽选择需要监控的范围。
2. 点击 **"Start Monitoring"**，程序将开始实时检测并执行点击。

## 依赖项
- opencv-python
- ultralytics (YOLO11)
- mss (Screen capture)
- pyautogui (Mouse control)
- PyQt6 (UI)
