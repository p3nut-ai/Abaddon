import sys
import os
import shutil
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton
)
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
import psutil
from glob import glob

class FileCopyThread(QThread):
    finished = pyqtSignal(str)

    def __init__(self, src, dest):
        super().__init__()
        self.src = src
        self.dest = dest

    def run(self):
        try:
            shutil.copy(self.src, self.dest)
            self.finished.emit("Malware copied successfully!")
        except Exception as e:
            self.finished.emit(f"Error copying file: {e}")

class ProgramDistributor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kaizens Solutions")
        self.setStyleSheet("background-color: black; color: white;")
        self.setWindowIcon(QIcon("1.png"))
        self.setup_ui()
        self.setCursor(Qt.PointingHandCursor)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.get_usb_devices)
        self.timer.start(2000)
        self.get_exe_files()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)

        left_column = QVBoxLayout()
        left_column.setAlignment(Qt.AlignCenter)

        logo_label = QLabel()
        pixmap = QPixmap("1.png")
        pixmap = pixmap.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        left_column.addWidget(logo_label)

        right_column = QVBoxLayout()
        right_column.setSpacing(20)
        right_column.setContentsMargins(40, 80, 20, 80)

        title = QLabel("Kaizens Project: Abaddon")
        title.setFont(QFont("Times", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        right_column.addWidget(title)

        self.program_dropdown = QComboBox()
        self.program_dropdown.addItem("Select a program")
        self.program_dropdown.setStyleSheet("""
            QComboBox {
                background-color: black;
                color: white;
                border: 1px solid white;
                border-radius: 5px;
                padding: 8px;
                height: 25px;
            }
            QComboBox::drop-down {
                border: none;
                width: 0px;
                height: 0px;
            }
        """)
        right_column.addWidget(self.program_dropdown)

        self.usb_dropdown = QComboBox()
        self.usb_dropdown.addItem("Select a USB drive")
        self.get_usb_devices()
        right_column.addWidget(self.usb_dropdown)

        self.selected_usb_label = QLabel("No USB selected")
        right_column.addWidget(self.selected_usb_label)

        self.usb_dropdown.currentTextChanged.connect(self.update_label)

        self.status_label = QLabel("")
        right_column.addWidget(self.status_label)

        self.upload_button = QPushButton("DEPLOY")
        self.upload_button.setEnabled(False)
        self.upload_button.setStyleSheet("""
            QPushButton {
                background-color: #ff6b6b;
                color: white;
                border: 1px solid #ff6b6b;
                padding: 10px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #ee5253;
            }
            QPushButton:disabled {
                background-color: black;
                color: gray;
                border: 1px solid gray;
            }
        """)
        self.upload_button.clicked.connect(self.upload_program)
        right_column.addWidget(self.upload_button)

        self.program_dropdown.currentIndexChanged.connect(self.check_selections)
        self.usb_dropdown.currentIndexChanged.connect(self.check_selections)

        main_layout.addLayout(left_column, 1)
        main_layout.addLayout(right_column, 2)

        self.setLayout(main_layout)

    def get_usb_devices(self):
        partitions = psutil.disk_partitions()
        usb_devices = []
        for partition in partitions:
            if 'removable' in partition.opts:
                usb_devices.append(partition.device)

        current_selection = self.usb_dropdown.currentText()
        self.usb_dropdown.blockSignals(True)
        self.usb_dropdown.clear()
        self.usb_dropdown.addItem("Select a USB drive")
        if usb_devices:
            self.usb_dropdown.addItems(usb_devices)
        else:
            self.usb_dropdown.addItem("No USB devices found.")

        if current_selection in usb_devices:
            self.usb_dropdown.setCurrentText(current_selection)
        elif usb_devices:
            self.usb_dropdown.setCurrentText(usb_devices[0])
            if hasattr(self, 'selected_usb_label'):
                self.selected_usb_label.setText(f"Selected USB: {usb_devices[0]}")

        self.usb_dropdown.blockSignals(False)

    def get_exe_files(self):
        proj_path = os.path.join(os.getcwd(), "projects")
        all_files = glob(os.path.join(proj_path, '**', '*'), recursive=True)
        self.program_dropdown.clear()
        self.program_dropdown.addItem("Select a program")
        for file in all_files:
            self.program_dropdown.addItem(os.path.basename(file))

    def update_label(self, text):
        if text != "Select a USB drive":
            self.selected_usb_label.setText(f"Selected USB: {text}")
        else:
            self.selected_usb_label.setText("No USB selected")

    def check_selections(self):
        program_selected = self.program_dropdown.currentIndex() > 0
        usb_selected = self.usb_dropdown.currentIndex() > 0
        self.upload_button.setEnabled(program_selected and usb_selected)

    def upload_program(self):
        selected_program = self.program_dropdown.currentText()
        selected_usb = self.usb_dropdown.currentText()

        proj_path = os.path.join(os.getcwd(), "projects/")
        all_files = glob(os.path.join(proj_path, '**', '*'), recursive=True)

        selected_program_path = None
        for file in all_files:
            if os.path.basename(file) == selected_program:
                selected_program_path = file
                break

        if selected_program_path and selected_usb != "Select a USB drive":
            usb_drive_path = os.path.join(selected_usb, selected_program)

            self.upload_button.setDisabled(True)
            self.upload_button.setText("DEPLOYING")

            self.file_copy_thread = FileCopyThread(selected_program_path, usb_drive_path)
            self.file_copy_thread.finished.connect(self.handle_copy_finished)
            self.file_copy_thread.start()
        else:
            print("No program or USB selected!")

    def handle_copy_finished(self, message):
        self.status_label.setText(message)
        self.upload_button.setEnabled(True)
        self.upload_button.setText("DEPLOY")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setStyleSheet("""
        QWidget {
            background-color: black;
            color: white;
        }
        QMainWindow::separator {
            background: black;
        }
        QToolBar {
            background: black;
        }
    """)

    window = ProgramDistributor()
    window.resize(800, 400)
    window.show()
    sys.exit(app.exec_())
