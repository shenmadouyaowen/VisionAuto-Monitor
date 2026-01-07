import sys
from PyQt6.QtWidgets import QApplication, QWidget, QRubberBand
from PyQt6.QtCore import QPoint, QRect, QSize, Qt

class AreaSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setWindowOpacity(0.3)
        self.setStyleSheet("background-color: black;")
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.showFullScreen()
        
        self.rubberBand = QRubberBand(QRubberBand.Shape.Rectangle, self)
        self.origin = QPoint()
        self.selected_rect = None

    def mousePressEvent(self, event):
        self.origin = event.pos()
        self.rubberBand.setGeometry(QRect(self.origin, QSize()))
        self.rubberBand.show()

    def mouseMoveEvent(self, event):
        self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        self.rubberBand.hide()
        rect = self.rubberBand.geometry()
        # Convert to screen coordinates if needed, but here we are full screen
        self.selected_rect = {
            'top': rect.top(),
            'left': rect.left(),
            'width': rect.width(),
            'height': rect.height()
        }
        print(f"Selected ROI: {self.selected_rect}")
        self.close()

def select_area():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    selector = AreaSelector()
    app.exec()
    return selector.selected_rect

if __name__ == "__main__":
    rect = select_area()
    print(rect)
