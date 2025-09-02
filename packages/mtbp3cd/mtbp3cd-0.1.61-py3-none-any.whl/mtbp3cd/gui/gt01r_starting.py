#  Copyright (C) 2025 Y Hsu <yh202109@gmail.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public license as published by
#  the Free software Foundation, either version 3 of the License, or
#  any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details
#
#  You should have received a copy of the GNU General Public license
#  along with this program. If not, see <https://www.gnu.org/license/>


import os
import pandas as pd
from datetime import datetime
from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator 

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, 
    QPushButton, QLabel,
    QFileDialog, QLineEdit
)

class TabStarting(QWidget):
    def __init__(self):
        super().__init__()
        layout_tab = QVBoxLayout()
        layout_tab.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.gt01_output_folder_path = None

        ###### Step 1
        self.tab_input1 = QLineEdit()
        self.tab_input1.setMaxLength(12)
        self.tab_input1.setValidator(
            QLineEdit().validator() or 
            QRegularExpressionValidator(QRegularExpression("[A-Za-z0-9]+"))
        )
        self.tab_input1.setText("output")
        self.tab_input1.setPlaceholderText("Enter up to 24 chars (A-Za-z0-9)")

        layout_tab_input1 = QVBoxLayout()
        layout_tab_input1.addWidget(QLabel("Step 1:\nType in a NEW output folder prefix (or leave blank if save to an existing folder):"))
        layout_tab_input1.addWidget(self.tab_input1)
        layout_tab.addLayout(layout_tab_input1)

        ###### Step 2
        self.tab_button_1 = QPushButton("Select Output Path")
        self.tab_button_1.clicked.connect(self.tab_button_1_f)

        layout_tab_button_1 = QVBoxLayout()
        layout_tab_button_1.addWidget(QLabel("Step 2:\nSelect output path:"))
        layout_tab_button_1.addWidget(self.tab_button_1)
        layout_tab.addLayout(layout_tab_button_1)

        ###### Step 3
        self.tab_button_2_label = QLabel("No folder selected")
        self.tab_button_2 = QPushButton("Create and Set Output Folder")
        self.tab_button_2.setEnabled(False)
        self.tab_button_2.clicked.connect(self.tab_button_2_f)

        layout_tab_button_2 = QVBoxLayout()
        layout_tab_button_2.addWidget(QLabel("Step 3:\nConfirm that outputs will be saved to this folder:"))
        layout_tab_button_2.addWidget(self.tab_button_2_label)
        layout_tab_button_2.addWidget(self.tab_button_2)
        layout_tab.addLayout(layout_tab_button_2)

        self.setLayout(layout_tab)

    def tab_button_1_f(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            if self.tab_input1.text():
                date_str = datetime.now().strftime("%Y%m%dT%H%M%S")
                folder2 = os.path.join(folder, f"{self.tab_input1.text()}_{date_str}")
            else:
                folder2 = folder
            if os.path.exists(folder2):
                existing_files = os.listdir(folder2)
                if existing_files:
                    self.tab_button_2_label.setText(
                        f"{folder2}\n\nWARNING: {len(existing_files)} file(s) exist and may be overwritten!\n\nOutput folder selected. Please continue to select input folder."
                    )
                else:
                    self.tab_button_2_label.setText(
                        f"{folder2}\n\nOutput folder selected. Please continue to select input folder."
                    )
                self.tab_button_2.setEnabled(False)
            else:
                self.tab_button_2_label.setText(folder2)
                self.tab_button_2.setEnabled(True)
            self.gt01_output_folder_path = folder2
        else:
            self.tab_button_2_label.setText("No folder selected")

    def tab_button_2_f(self):
        folder_path = self.gt01_output_folder_path
        if folder_path:
            try:
                os.makedirs(folder_path, exist_ok=True)
                self.tab_button_2_label.setText(f"{folder_path}\n\nOutput folder created. Continue to select input folder.")
                self.tab_button_2.setEnabled(False)
            except Exception as e:
                self.tab_button_2_label.setText(f"Error: {str(e)}")
                self.gt01_output_folder_path = None
        else:
            self.tab_button_2_label.setText("No folder selected")

if __name__ == "__main__":
    pass