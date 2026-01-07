import cv2
import os
import sys
# 添加当前目录到路径以确保能找到 src
sys.path.append(os.getcwd())
from src.core.detector import YOLO11Detector
import random
from pathlib import Path

def test_inference():
    # 1. 初始化检测器，使用刚才训练好的最佳权重
    model_path = 'models/best.pt'
    if not os.path.exists(model_path):
        print(f"错误: 找不到模型文件 {model_path}")
        return

    print(f"正在加载模型: {model_path}")
    detector = YOLO11Detector(model_path)

    # 2. 随机选择一张训练集中的图片进行测试
    dataset_dir = Path('dataset/images/train')
    test_images = list(dataset_dir.glob('*.jpg'))
    
    if not test_images:
        print("错误: dataset/images/train 目录下没有找到测试图片")
        return

    test_img_path = str(random.choice(test_images))
    print(f"正在测试图片: {test_img_path}")

    # 3. 执行检测
    img = cv2.imread(test_img_path)
    detections = detector.detect(img, conf=0.5)

    print(f"检测到 {len(detections)} 个目标:")
    for i, det in enumerate(detections):
        print(f"  目标 {i+1}: 类别={det['class']}, 置信度={det['conf']:.2f}, 坐标={det['box']}")
        
        # 在图上画框（可选，这里仅打印信息）
        x1, y1, x2, y2 = map(int, det['box'])
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(img, f"retry {det['conf']:.2f}", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # 4. 保存测试结果图
    output_path = 'test_result.jpg'
    cv2.imwrite(output_path, img)
    print(f"测试结果已保存至: {output_path}")

if __name__ == "__main__":
    test_inference()
