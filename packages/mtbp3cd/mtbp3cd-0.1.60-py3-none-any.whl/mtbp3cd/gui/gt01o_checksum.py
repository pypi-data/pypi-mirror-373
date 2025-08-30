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
import hashlib
from datetime import datetime
from PyQt6.QtCore import Qt

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, 
    QPushButton, QLabel,
    QHBoxLayout, QComboBox,
    QTabWidget, QTextEdit,
    QFileDialog
)

class TabChecksum(QWidget):
    def __init__(self, _p):
        super().__init__()
        layout_tab = QVBoxLayout()
        layout_tab.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.selected_checksum_file = None

        # Label and ComboBox for checksum type
        tab_label1 = QLabel("Checksum Type:")
        self.checksum_type = QComboBox()
        self.checksum_type.addItems(["SHA-512", "SHA-256", "MD5"])

        layout_tab_input1 = QHBoxLayout()
        layout_tab_input1.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_tab_input1.addWidget(tab_label1)
        layout_tab_input1.addWidget(self.checksum_type)
        layout_tab.addLayout(layout_tab_input1)

        # Export Button
        self.tab_button_1 = QPushButton("Generate")
        self.tab_button_1.clicked.connect(lambda: self.tab_button_1_f(_p))
        self.tab_button_2 = QPushButton("Select File")
        self.tab_button_2.clicked.connect(self.tab_button_2_f)
        self.tab_button_3 = QPushButton("Check")
        self.tab_button_3.clicked.connect(lambda: self.tab_button_3_f(_p))

        layout_tab_button = QHBoxLayout()
        layout_tab_button.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_tab_button.addWidget(self.tab_button_1)
        layout_tab_button.addWidget(self.tab_button_2)
        layout_tab_button.addWidget(self.tab_button_3)
        layout_tab.addLayout(layout_tab_button)

        # Tabset to display selected file and check results
        self.tab_tabs = QTabWidget()
        self.tab_tabs.tabBar().setVisible(False)
        self.tab_tabs_text_1 = QTextEdit()
        self.tab_tabs_text_1.setReadOnly(True)
        self.tab_tabs.addTab(self.tab_tabs_text_1, "Check Results")

        layout_tab.addWidget(self.tab_tabs)
        self.setLayout(layout_tab)

    def tab_button_1_f(self, _p):
        folder_path = getattr(_p.tab_folder, "gt01_input_folder_path", None)
        output_folder = getattr(_p.tab_starting, "gt01_output_folder_path", None)
        if not folder_path or not os.path.isdir(folder_path):
            self.tab_tabs_text_1.setPlainText("No valid folder selected.")
            return
        if not output_folder or not os.path.isdir(output_folder):
            self.tab_tabs_text_1.setPlainText("No valid output folder.")
            return

        algo = self.checksum_type.currentText()
        hash_func = {
            "SHA-512": hashlib.sha512,
            "SHA-256": hashlib.sha256,
            "MD5": hashlib.md5
        }.get(algo)

        results = []
        
        try:
            for root, _, files in os.walk(folder_path):
                if os.path.abspath(root).startswith(os.path.abspath(output_folder)):
                    continue
                for fname in files:
                    fpath = os.path.join(root, fname)
                    try:
                        with open(fpath, "rb") as f:
                            hasher = hash_func()
                            while True:
                                data = f.read(8192)
                                if not data:
                                    break
                                hasher.update(data)
                            checksum = hasher.hexdigest()
                        rel_path = os.path.relpath(fpath, folder_path)
                        results.append(f"{checksum}  {rel_path}")
                    except Exception as fe:
                        results.append(f"Error reading {fname}: {str(fe)}")

            ext = {
                "SHA-512": ".sha512",
                "SHA-256": ".sha256",
                "MD5": ".md5"
            }[algo]
            out_file = os.path.join(output_folder, f"checksums{ext}")
            if os.path.exists(out_file):
                dt_str = getattr(_p.tab_folder, "tab_folder_meta_json", {}).get("scan_time", datetime.now().strftime("%Y%m%dT%H%M%S"))
                dt_str = dt_str.replace(":", "").replace("-", "").replace(" ", "T")
                out_file = os.path.join(output_folder, f"checksums_{dt_str}{ext}")
            with open(out_file, "w") as outf:
                outf.write("\n".join(results))

            self.tab_tabs_text_1.setPlainText(f"Checksums saved to:\n{out_file}")
        except Exception as e:
            self.tab_tabs_text_1.setPlainText(f"Error: {str(e)}")

    def tab_button_2_f(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("Checksum Files (*.sha512 *.sha256 *.md5 *.txt);;All Files (*)")
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                selected_file = selected_files[0]
                try:
                    with open(selected_file, "r", encoding="utf-8") as f:
                        lines = []
                        for i in range(10):
                            line = f.readline()
                            if not line:
                                break
                            lines.append(line.rstrip('\n'))
                        if i == 9 and f.readline():
                            lines.append(f"(viewing up to 10 lines)")
                    self.tab_tabs_text_1.setPlainText("\n".join(lines))
                    self.selected_checksum_file = selected_file
                except Exception as e:
                    self.tab_tabs_text_1.setPlainText(f"Error reading file: {e}")

    def tab_button_3_f(self, _p):
        if not self.selected_checksum_file:
            self.tab_tabs_text_1.setPlainText("No checksum file selected. Please use 'Select' to select one.")
            return

        folder_path = getattr(_p.tab_folder, "gt01_input_folder_path", None)
        if not folder_path or not os.path.isdir(folder_path):
            self.tab_tabs_text_1.setPlainText("No valid folder selected.")
            return

        algo = self.checksum_type.currentText()
        hash_func = {
            "SHA-512": hashlib.sha512,
            "SHA-256": hashlib.sha256,
            "MD5": hashlib.md5
        }[algo]

        # Read checksums from file
        checksums = {}
        try:
            with open(self.selected_checksum_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    parts = line.split(None, 1)
                    if len(parts) == 2:
                        checksum, rel_path = parts
                        checksums[rel_path.strip()] = checksum.strip()
        except Exception as e:
            self.tab_tabs_text_1.setPlainText(f"Error reading checksum file: {e}")
            return

        results = []
        for rel_path, expected_checksum in checksums.items():
            abs_path = os.path.join(folder_path, rel_path)
            if not os.path.isfile(abs_path):
                results.append(f"Missing: {rel_path}")
                continue
            try:
                with open(abs_path, "rb") as f:
                    hasher = hash_func()
                    while True:
                        data = f.read(8192)
                        if not data:
                            break
                        hasher.update(data)
                    actual_checksum = hasher.hexdigest()
                if actual_checksum.lower() == expected_checksum.lower():
                    results.append(f"OK: {rel_path}")
                else:
                    results.append(f"FAIL: {rel_path} (expected {expected_checksum}, got {actual_checksum})")
            except Exception as e:
                results.append(f"Error reading {rel_path}: {e}")

        self.tab_tabs_text_1.setPlainText("\n".join(results) if results else "No files to check.")


if __name__ == "__main__":
    pass