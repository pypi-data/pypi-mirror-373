# pylint: disable=C0114, C0115, C0116, E0611, R0915, R0902
import os
import numpy as np
from PySide6.QtWidgets import (QHBoxLayout, QPushButton, QLabel, QCheckBox, QSpinBox,
                               QMessageBox)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from .. config.gui_constants import gui_constants
from .. config.constants import constants
from .. algorithms.utils import read_img, extension_tif_jpg
from .. algorithms.stack import get_bunches
from .select_path_widget import create_select_file_paths_widget
from .base_form_dialog import BaseFormDialog

DEFAULT_NO_COUNT_LABEL = " - "


class NewProjectDialog(BaseFormDialog):
    def __init__(self, parent=None):
        super().__init__("New Project", parent)
        self.create_form()
        button_box = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.setFocus()
        cancel_button = QPushButton("Cancel")
        button_box.addWidget(ok_button)
        button_box.addWidget(cancel_button)
        self.add_row_to_layout(button_box)
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        self.n_image_files = 0

    def expert(self):
        return self.parent().expert_options

    def add_bold_label(self, label):
        label = QLabel(label)
        label.setStyleSheet("font-weight: bold")
        self.form_layout.addRow(label)

    def add_label(self, label):
        label = QLabel(label)
        self.form_layout.addRow(label)

    def create_form(self):
        icon_path = f"{os.path.dirname(__file__)}/ico/shinestacker.png"
        app_icon = QIcon(icon_path)
        icon_pixmap = app_icon.pixmap(128, 128)
        icon_label = QLabel()
        icon_label.setPixmap(icon_pixmap)
        icon_label.setAlignment(Qt.AlignCenter)
        self.form_layout.addRow(icon_label)
        spacer = QLabel("")
        spacer.setFixedHeight(10)
        self.form_layout.addRow(spacer)

        self.input_folder, container = create_select_file_paths_widget(
            '', 'input files folder', 'input files folder')
        self.input_folder.textChanged.connect(self.update_bunches_label)
        self.noise_detection = QCheckBox()
        self.noise_detection.setChecked(gui_constants.NEW_PROJECT_NOISE_DETECTION)
        self.vignetting_correction = QCheckBox()
        self.vignetting_correction.setChecked(gui_constants.NEW_PROJECT_VIGNETTING_CORRECTION)
        self.align_frames = QCheckBox()
        self.align_frames.setChecked(gui_constants.NEW_PROJECT_ALIGN_FRAMES)
        self.balance_frames = QCheckBox()
        self.balance_frames.setChecked(gui_constants.NEW_PROJECT_BALANCE_FRAMES)

        self.bunch_stack = QCheckBox()
        self.bunch_stack.setChecked(gui_constants.NEW_PROJECT_BUNCH_STACK)
        self.bunch_frames = QSpinBox()
        bunch_frames_range = gui_constants.NEW_PROJECT_BUNCH_FRAMES
        self.bunch_frames.setRange(bunch_frames_range['min'], bunch_frames_range['max'])
        self.bunch_frames.setValue(constants.DEFAULT_FRAMES)
        self.bunch_overlap = QSpinBox()
        bunch_overlap_range = gui_constants.NEW_PROJECT_BUNCH_OVERLAP
        self.bunch_overlap.setRange(bunch_overlap_range['min'], bunch_overlap_range['max'])
        self.bunch_overlap.setValue(constants.DEFAULT_OVERLAP)
        self.bunches_label = QLabel(DEFAULT_NO_COUNT_LABEL)
        self.frames_label = QLabel(DEFAULT_NO_COUNT_LABEL)

        self.update_bunch_options(gui_constants.NEW_PROJECT_BUNCH_STACK)
        self.bunch_stack.toggled.connect(self.update_bunch_options)
        self.bunch_frames.valueChanged.connect(self.update_bunches_label)
        self.bunch_overlap.valueChanged.connect(self.update_bunches_label)

        self.focus_stack_pyramid = QCheckBox()
        self.focus_stack_pyramid.setChecked(gui_constants.NEW_PROJECT_FOCUS_STACK_PYRAMID)
        self.focus_stack_depth_map = QCheckBox()
        self.focus_stack_depth_map.setChecked(gui_constants.NEW_PROJECT_FOCUS_STACK_DEPTH_MAP)
        self.multi_layer = QCheckBox()
        self.multi_layer.setChecked(gui_constants.NEW_PROJECT_MULTI_LAYER)

        self.add_bold_label("1️⃣ Select input folder, all images therein will be merged. ")
        self.form_layout.addRow("Input folder:", container)
        self.form_layout.addRow("Number of frames: ", self.frames_label)
        self.add_label("")
        self.add_bold_label("2️⃣ Select basic options.")
        if self.expert():
            self.form_layout.addRow("Automatic noise detection:", self.noise_detection)
            self.form_layout.addRow("Vignetting correction:", self.vignetting_correction)
        self.form_layout.addRow("Align layers:", self.align_frames)
        self.form_layout.addRow("Balance layers:", self.balance_frames)
        self.form_layout.addRow("Bunch stack:", self.bunch_stack)
        self.form_layout.addRow("Bunch frames:", self.bunch_frames)
        self.form_layout.addRow("Bunch overlap:", self.bunch_overlap)
        self.form_layout.addRow("Number of bunches: ", self.bunches_label)
        if self.expert():
            self.form_layout.addRow("Focus stack (pyramid):", self.focus_stack_pyramid)
            self.form_layout.addRow("Focus stack (depth map):", self.focus_stack_depth_map)
        else:
            self.form_layout.addRow("Focus stack:", self.focus_stack_pyramid)
        if self.expert():
            self.form_layout.addRow("Save multi layer TIFF:", self.multi_layer)
        self.add_label("")
        self.add_bold_label("3️⃣ Push 🆗 for further options, then press ▶️ to run.")
        self.add_label("")
        self.add_label("4️⃣ "
                       "Select: <b>View</b> > <b>Expert options</b> "
                       "to unlock advanced configuration.")

    def update_bunch_options(self, checked):
        self.bunch_frames.setEnabled(checked)
        self.bunch_overlap.setEnabled(checked)
        self.update_bunches_label()

    def update_bunches_label(self):
        if not self.input_folder.text():
            return

        def count_image_files(path):
            if path == '' or not os.path.isdir(path):
                return 0
            count = 0
            for filename in os.listdir(path):
                if extension_tif_jpg(filename):
                    count += 1
            return count

        self.n_image_files = count_image_files(self.input_folder.text())
        if self.n_image_files == 0:
            self.bunches_label.setText(DEFAULT_NO_COUNT_LABEL)
            self.frames_label.setText(DEFAULT_NO_COUNT_LABEL)
            return
        self.frames_label.setText(f"{self.n_image_files}")
        if self.bunch_stack.isChecked():
            bunches = get_bunches(list(range(self.n_image_files)),
                                  self.bunch_frames.value(),
                                  self.bunch_overlap.value())
            self.bunches_label.setText(f"{len(bunches)}")
        else:
            self.bunches_label.setText(DEFAULT_NO_COUNT_LABEL)

    def accept(self):
        input_folder = self.input_folder.text()
        if not input_folder:
            QMessageBox.warning(self, "Input Required", "Please select an input folder")
            return
        if not os.path.exists(input_folder):
            QMessageBox.warning(self, "Invalid Path", "The specified folder does not exist")
            return
        if not os.path.isdir(input_folder):
            QMessageBox.warning(self, "Invalid Path", "The specified path is not a folder")
            return
        if len(input_folder.split('/')) < 2:
            QMessageBox.warning(self, "Invalid Path", "The path must have a parent folder")
            return
        if self.n_image_files > 0 and not self.bunch_stack.isChecked():
            path = self.input_folder.text()
            files = os.listdir(path)
            file_path = None
            for filename in files:
                full_path = os.path.join(path, filename)
                if extension_tif_jpg(full_path):
                    file_path = full_path
                    break
            if file_path is None:
                QMessageBox.warning(
                    self, "Invalid input", "Could not find images now in the selected path")
                return
            img = read_img(file_path)
            height, width = img.shape[:2]
            n_bytes = 1 if img.dtype == np.uint8 else 2
            n_bits = 8 if img.dtype == np.uint8 else 16
            n_gbytes = float(n_bytes * height * width * self.n_image_files) / constants.ONE_GIGA
            print("GBytes: ", n_gbytes)
            if n_gbytes > 1 and not self.bunch_stack.isChecked():
                msg = QMessageBox()
                msg.setStyleSheet("""
                    QMessageBox {
                        min-width: 600px;
                        font-weight: bold;
                        font-size: 14px;
                    }
                    QMessageBox QLabel#qt_msgbox_informativelabel {
                        font-weight: normal;
                        font-size: 14px;
                        color: #555555;
                    }
                """)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Too many frames")
                msg.setText(f"You selected {self.n_image_files} images "
                            f"with resolution {width}×{height} pixels, {n_bits} bits depth. "
                            "Processing may require a significant amount "
                            "of memory or I/O buffering.\n\n"
                            "Continue anyway?")
                msg.setInformativeText("You may consider to split the processing "
                                       " using a bunch stack to reduce memory usage.\n\n"
                                       '✅ Check the option "Bunch stack".\n\n'
                                       "➡️ Check expert options for the stacking algorithm."
                                       'Go to "View" > "Expert Options".'
                                       )
                msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                msg.setDefaultButton(QMessageBox.Cancel)
                if msg.exec_() != QMessageBox.Ok:
                    return
        super().accept()

    def get_input_folder(self):
        return self.input_folder.text()

    def get_noise_detection(self):
        return self.noise_detection.isChecked()

    def get_vignetting_correction(self):
        return self.vignetting_correction.isChecked()

    def get_align_frames(self):
        return self.align_frames.isChecked()

    def get_balance_frames(self):
        return self.balance_frames.isChecked()

    def get_bunch_stack(self):
        return self.bunch_stack.isChecked()

    def get_bunch_frames(self):
        return self.bunch_frames.value()

    def get_bunch_overlap(self):
        return self.bunch_overlap.value()

    def get_focus_stack_pyramid(self):
        return self.focus_stack_pyramid.isChecked()

    def get_focus_stack_depth_map(self):
        return self.focus_stack_depth_map.isChecked()

    def get_multi_layer(self):
        return self.multi_layer.isChecked()
