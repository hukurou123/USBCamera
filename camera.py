import sys
import cv2
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QComboBox
from PySide6.QtCore import QTimer
from PySide6.QtGui import QImage, QPixmap

class CameraSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("カメラ選択ビューア")
        self.setFixedSize(680, 540)

        self.layout = QVBoxLayout()
        self.combo = QComboBox()
        self.label = QLabel("カメラ映像")
        self.label.setFixedSize(640, 480)

        self.layout.addWidget(self.combo)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        self.cap = None
        self.populate_cameras()
        self.combo.currentIndexChanged.connect(self.change_camera)
        self.change_camera(0)

    def populate_cameras(self, max_devices=5):
        for i in range(max_devices):
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                self.combo.addItem(f"Camera {i}", userData=i)
                cap.release()

    def change_camera(self, index):
        if self.cap:
            self.cap.release()
        cam_index = self.combo.itemData(index)
        self.cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
        self.timer.start(30)

    def update_frame(self):
        if not self.cap:
            return
        ret, frame = self.cap.read()
        if ret:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
            self.label.setPixmap(QPixmap.fromImage(img))

    def closeEvent(self, event):
        if self.cap:
            self.cap.release()
        self.timer.stop()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = CameraSelector()
    viewer.show()
    sys.exit(app.exec())
