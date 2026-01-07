import sys
import threading
import time
import mss
import numpy as np
import cv2
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QLabel, QGroupBox, QHBoxLayout)
from PyQt6.QtCore import Qt, pyqtSignal

from src.ui.selector import AreaSelector
from src.core.capturer import ScreenCapturer
from src.core.detector import YOLO11Detector
from src.core.executor import ActionExecutor

class Dashboard(QMainWindow):
    status_update = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("VisionAuto-Monitor (YOLO11)")
        self.setMinimumSize(400, 300)
        
        self.capturer = ScreenCapturer()
        self.executor = ActionExecutor()
        self.detector = None # Load on demand or start
        self.roi = None
        self.monitoring = False
        
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        # Region selection
        roi_group = QGroupBox("Monitoring Region")
        roi_layout = QHBoxLayout()
        self.roi_label = QLabel("No region selected")
        select_btn = QPushButton("Select Region")
        select_btn.clicked.connect(self.start_selection)
        roi_layout.addWidget(self.roi_label)
        roi_layout.addWidget(select_btn)
        roi_group.setLayout(roi_layout)
        
        # Controls
        control_group = QGroupBox("Detection Controls")
        control_layout = QVBoxLayout()
        self.status_label = QLabel("Status: Idle")
        self.start_btn = QPushButton("Start Monitoring")
        self.start_btn.clicked.connect(self.toggle_monitoring)
        self.start_btn.setEnabled(False)
        control_layout.addWidget(self.status_label)
        control_layout.addWidget(self.start_btn)
        control_group.setLayout(control_layout)
        
        layout.addWidget(roi_group)
        layout.addWidget(control_group)
        
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        self.status_update.connect(self.status_label.setText)

    def start_selection(self):
        self.selector = AreaSelector()
        self.selector.destroyed.connect(self.on_selection_finished)
        self.selector.show()

    def on_selection_finished(self):
        if self.selector.selected_rect:
            self.roi = self.selector.selected_rect
            self.roi_label.setText(f"ROI: {self.roi['width']}x{self.roi['height']} at ({self.roi['left']}, {self.roi['top']})")
            self.start_btn.setEnabled(True)
            self.raise_()
            self.activateWindow()

    def toggle_monitoring(self):
        if not self.monitoring:
            if not self.roi:
                return
            
            try:
                if self.detector is None:
                    self.status_update.emit("Status: Loading YOLO11...")
                    # Delay loading to background thread? For now, simple
                    self.detector = YOLO11Detector()
            except Exception as e:
                self.status_update.emit(f"Status: Error loading model: {e}")
                return

            self.monitoring = True
            self.start_btn.setText("Stop Monitoring")
            self.status_update.emit("Status: Monitoring...")
            
            self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
            self.monitor_thread.start()
        else:
            self.monitoring = False
            self.start_btn.setText("Start Monitoring")
            self.status_update.emit("Status: Stopped")

    def monitor_loop(self):
        # Create a local mss instance for this thread
        retry_count = 0
        no_target_count = 0
        last_click_time = 0
        
        with mss.mss() as sct:
            while self.monitoring:
                # Use local sct instead of self.capturer.sct which was created in main thread
                screenshot = sct.grab(self.roi)
                img = np.array(screenshot)
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                
                detections = self.detector.detect(img, conf=0.3)
                
                # Check for Error State (Class 1) or excessive retries
                has_error = any(d['class'] == 1 for d in detections)
                action_btn = next((d for d in detections if d['class'] == 0), None)
                
                if has_error:
                    self.status_update.emit("Status: Error detected! Stopping.")
                    self.monitoring = False
                    self.start_btn.setText("Start Monitoring")
                    break
                
                if action_btn:
                    no_target_count = 0
                    current_time = time.time()
                    
                    # Offset calculation
                    cx, cy = self.detector.get_center(action_btn['box'])
                    
                    # 居中优化：如果按钮太靠近顶部或底部，先滚动
                    roi_h = self.roi['height']
                    margin = roi_h * 0.2
                    if cy < margin:
                        self.status_update.emit("Status: Target too high, scrolling up...")
                        self.executor.scroll(300)
                        time.sleep(0.5)
                    elif cy > roi_h - margin:
                        self.status_update.emit("Status: Target too low, scrolling down...")
                        self.executor.scroll(-300)
                        time.sleep(0.5)

                    # If we find a button again quickly, increment count
                    if current_time - last_click_time < 5: 
                        retry_count += 1
                        self.status_update.emit(f"Status: Retry {retry_count}/5...")
                    else:
                        retry_count = 1
                    
                    if retry_count > 5:
                        self.status_update.emit("Status: Max retries reached. Stopping.")
                        self.monitoring = False
                        self.start_btn.setText("Start Monitoring")
                        break
                        
                    screen_x = int(self.roi['left'] + cx)
                    screen_y = int(self.roi['top'] + cy)
                    
                    self.status_update.emit(f"Status: Clicking ({screen_x}, {screen_y}) | Attempt {retry_count}")
                    self.executor.click_at(screen_x, screen_y)
                    last_click_time = time.time()
                    
                    # Cooldown to avoid double clicks
                    time.sleep(3)
                else:
                    no_target_count += 1
                    # Reset count if button disappears (success or manual intervention)
                    if time.time() - last_click_time > 10:
                        retry_count = 0
                    
                    # 滚动寻标逻辑：连续约 5 秒找不到目标，尝试向下滚动
                    if no_target_count >= 10:
                        self.status_update.emit("Status: No target found, searching (scroll down)...")
                        self.executor.scroll(-500)
                        no_target_count = 0
                        time.sleep(1.0)
                
                time.sleep(0.5)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Dashboard()
    window.show()
    sys.exit(app.exec())
