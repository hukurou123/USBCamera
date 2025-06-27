import sys
import time
import cv2
import math
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QGridLayout
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QTimer


class MultiCameraViewer(QWidget):
    def __init__(self, camera_indices):
        super().__init__()
        self.setWindowTitle("Multi Camera Viewer")

        self.labels = []
        self.captures = []

        layout = QGridLayout()
        grid_cols = math.ceil(math.sqrt(len(camera_indices)))

        for idx, cam_index in enumerate(camera_indices):
            row = idx // grid_cols
            col = idx % grid_cols

            label = QLabel(f"カメラ {cam_index}")
            label.setFixedSize(480, 360)  # ← 小さくした！
            self.labels.append(label)
            print("camera opened...")
            cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
            self.captures.append(cap)

            layout.addWidget(label, row, col)

        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frames)
        self.timer.start(30)

    def update_frames(self):
        for i, cap in enumerate(self.captures):
            ret, frame = cap.read()
            if ret:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb.shape
                img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
                self.labels[i].setPixmap(QPixmap.fromImage(img))

    def closeEvent(self, event):
        for cap in self.captures:
            cap.release()


def find_available_cameras(max_devices=10):
    available = []
    for i in range(max_devices):
        print("camera find...\n")
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if cap is not None:
            ret, frame = cap.read()
            if ret:
                available.append(i)
            cap.release()
    print("find complete\n")
    return available


def try_open_camera(index):
    for backend in [cv2.CAP_MSMF, cv2.CAP_DSHOW, cv2.CAP_ANY]:
        print("backend try")
        cap = cv2.VideoCapture(index, backend)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"✅ Camera {index} opened with backend {backend}")
                return cap
            cap.release()
    print(f"❌ Camera {index} could not be opened with any backend.")
    return None


if __name__ == "__main__":
    available_cameras = find_available_cameras()
    if not available_cameras:
        print("⚠️ 使用可能なカメラが見つかりませんでした。")
        sys.exit(1)

    app = QApplication(sys.argv)
    viewer = MultiCameraViewer(available_cameras)
    viewer.show()
    sys.exit(app.exec())
