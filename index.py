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
        self.setWindowIcon(QIcon("1.png"))  # Replace "1.png" with the path to your logo image



        # self.setFixedSize(800, 400)  # Set a fixed size for the window
        # self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint)  # Remove maximize and fullscreen options

        # Set up the UI
        self.setup_ui()

        # Set the cursor for the entire window
        self.setCursor(Qt.PointingHandCursor)  # Set the cursor style



        # Timer to refresh USB devices every 2 seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.get_usb_devices)
        self.timer.start(2000)

        # Load .exe files on initialization
        self.get_exe_files()

    def setup_ui(self):
        # Layout setup
        main_layout = QHBoxLayout(self)

        # Left column: Logo
        left_column = QVBoxLayout()
        left_column.setAlignment(Qt.AlignCenter)

        # Load and set the image as the logo
        logo_label = QLabel()
        pixmap = QPixmap("1.png")  # Replace "1.png" with the path to your image
        pixmap = pixmap.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        left_column.addWidget(logo_label)

        # Right column: Title, Dropdowns, and Button
        right_column = QVBoxLayout()
        right_column.setSpacing(20)
        right_column.setContentsMargins(40, 80, 20, 80)  # Add padding around the right column

        # Title
        title = QLabel("Kaizens Project: Abaddon")
        title.setFont(QFont("Times", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        right_column.addWidget(title)

        # Dropdown menus
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

        self.get_usb_devices()  # Populate the dropdown based on available USB devices
        right_column.addWidget(self.usb_dropdown)

        # Initialize the selected USB label
        self.selected_usb_label = QLabel("No USB selected")
        right_column.addWidget(self.selected_usb_label)

        self.usb_dropdown.currentTextChanged.connect(self.update_label)

        # Status label for copy completion
        self.status_label = QLabel("")
        right_column.addWidget(self.status_label)

        # Button
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

        # Connect dropdown signals to enable/disable the button
        self.program_dropdown.currentIndexChanged.connect(self.check_selections)
        self.usb_dropdown.currentIndexChanged.connect(self.check_selections)

        # Add columns to the main layout
        main_layout.addLayout(left_column, 1)
        main_layout.addLayout(right_column, 2)

        # Set the main layout for the window
        self.setLayout(main_layout)

    def get_usb_devices(self):
        """Detect USB devices and add them to the dropdown."""
        partitions = psutil.disk_partitions()
        usb_devices = []

        # Loop through partitions and check for removable devices (USB)
        for partition in partitions:
            if 'removable' in partition.opts:
                usb_devices.append(partition.device)

        # Save the current selection before updating the dropdown
        current_selection = self.usb_dropdown.currentText()

        # Temporarily disconnect the signal to avoid resetting the selection
        self.usb_dropdown.blockSignals(True)

        # Clear and update the dropdown with the new USB devices
        self.usb_dropdown.clear()  # Clear old items
        self.usb_dropdown.addItem("Select a USB drive")  # Default option
        if usb_devices:
            self.usb_dropdown.addItems(usb_devices)
        else:
            self.usb_dropdown.addItem("No USB devices found.")

        # Restore the previously selected value, if possible
        if current_selection in usb_devices:
            self.usb_dropdown.setCurrentText(current_selection)
        elif usb_devices:
            self.usb_dropdown.setCurrentText(usb_devices[0])
            # Check if selected_usb_label is initialized before using it
            if hasattr(self, 'selected_usb_label'):
                self.selected_usb_label.setText(f"Selected USB: {usb_devices[0]}")  # Update label with selected USB

        # Reconnect the signal
        self.usb_dropdown.blockSignals(False)

    def get_exe_files(self):
        """Get all .exe files from system and add them to the program dropdown."""
        proj_path = os.path.join(os.getcwd(), "projects")
        all_files = glob(os.path.join(proj_path, '**', '*'), recursive=True)

        # Add .exe files to the dropdown
        self.program_dropdown.clear()  # Clear old items
        self.program_dropdown.addItem("Select a program")  # Default option
        for file in all_files:
            self.program_dropdown.addItem(os.path.basename(file))  # Add file name (without path)

    def update_label(self, text):
        """Update the label when a USB device is selected."""
        if text != "Select a USB drive":
            self.selected_usb_label.setText(f"Selected USB: {text}")
        else:
            self.selected_usb_label.setText("No USB selected")

    def check_selections(self):
        """Check if both a program and a USB are selected, and enable the button if true."""
        program_selected = self.program_dropdown.currentIndex() > 0
        usb_selected = self.usb_dropdown.currentIndex() > 0
        self.upload_button.setEnabled(program_selected and usb_selected)

    def upload_program(self):
        """Simulate the process of copying the selected program to the selected USB drive."""
        selected_program = self.program_dropdown.currentText()
        selected_usb = self.usb_dropdown.currentText()

        # Get the full path of the selected program file
        proj_path = os.path.join(os.getcwd(), "projects/")  # Assuming this is the folder where the programs are stored
        all_files = glob(os.path.join(proj_path, '**', '*'), recursive=True)  # Get all files in the folder

        selected_program_path = None
        for file in all_files:
            if os.path.basename(file) == selected_program:  # Compare with the selected program (file name)
                selected_program_path = file
                break

        if selected_program_path and selected_usb != "Select a USB drive":
            usb_drive_path = os.path.join(selected_usb, selected_program)

            # Disable the upload button and change text to DEPLOYING
            self.upload_button.setDisabled(True)
            self.upload_button.setText("DEPLOYING")

            # Create and start the file copy thread
            self.file_copy_thread = FileCopyThread(selected_program_path, usb_drive_path)
            self.file_copy_thread.finished.connect(self.handle_copy_finished)
            self.file_copy_thread.start()
        else:
            print("No program or USB selected!")

    def handle_copy_finished(self, message):
        """Handle the completion of the file copy operation."""
        self.status_label.setText(message)
        # Re-enable the upload button and change text back to DEPLOY
        self.upload_button.setEnabled(True)
        self.upload_button.setText("DEPLOY")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set the application's title bar color to black
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
    sys.exit(app.exec())
