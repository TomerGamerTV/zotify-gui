from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QImage, QPixmap
import requests

def set_button_icon(btn, icon_path):
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap(icon_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    btn.setIcon(icon)


def set_label_image(label, path_or_url, from_url=False):
    if from_url:
        try:
            response = requests.get(path_or_url, timeout=5)
            response.raise_for_status()
            image = QImage()
            image.loadFromData(response.content)
            pixmap = QPixmap.fromImage(image)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching image: {e}")
            pixmap = QPixmap("Resources/cover_default.jpg") # fallback
    else:
        pixmap = QPixmap(path_or_url)

    if not pixmap.isNull():
        label.setPixmap(pixmap)
        label.setScaledContents(True)
        label.show()
