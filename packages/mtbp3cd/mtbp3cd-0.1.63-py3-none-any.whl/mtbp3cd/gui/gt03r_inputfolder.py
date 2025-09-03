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
from PyQt6.QtCore import Qt
from datetime import datetime
from mtbp3cd.util.lsr import LsrTree
import mtbp3cd.gui
import json

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, 
    QPushButton, QLabel,
    QTableWidget, QFileDialog,
    QTabWidget, QHBoxLayout,
    QTableWidgetItem, QListWidget
)

class TabInput(QWidget):
    def __init__(self, _p):
        super().__init__()
        self._p = _p

        self.tab_button_1 = QPushButton("Select Tabulation Folder")
        self.tab_button_1.setEnabled(True)
        self.tab_button_1.clicked.connect(self.tab_button_1_f)

        self.tab_button_2 = QPushButton("Select Analysis Folder")
        self.tab_button_2.setEnabled(True)
        self.tab_button_2.clicked.connect(self.tab_button_2_f)

        self.tab_button_3 = QPushButton("Save Logs")
        self.tab_button_3.setEnabled(True)
        self.tab_button_3.clicked.connect(self.tab_button_3_f)

        layout_button = QHBoxLayout()
        layout_button.addWidget(self.tab_button_1)
        layout_button.addWidget(self.tab_button_2)
        layout_button.addWidget(self.tab_button_3)

        # BOX - tabs
        self.tabs = QTabWidget()
        self.tabs_sd = QTabWidget()
        self.tabs_ad = QTabWidget()
        self.tab_sd_meta = QWidget()
        self.tab_sd_tree = QWidget()
        self.tab_ad_meta = QWidget()
        self.tab_ad_tree = QWidget()

        # BOX - Tab Meta 
        self.tab_sd_meta_table = QTableWidget()
        self.tab_sd_meta_table.setColumnCount(2)
        self.tab_sd_meta_table.setHorizontalHeaderLabels(["Key", "Value"])
        self.tab_sd_meta_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tab_sd_meta_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.tab_sd_meta_table.setStyleSheet("font-family: 'Courier New', monospace;")

        layout_tab_sd_meta = QVBoxLayout()
        layout_tab_sd_meta.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_tab_sd_meta.addWidget(self.tab_sd_meta_table)
        self.tab_sd_meta.setLayout(layout_tab_sd_meta)

        self.tab_ad_meta_table = QTableWidget()
        self.tab_ad_meta_table.setColumnCount(2)
        self.tab_ad_meta_table.setHorizontalHeaderLabels(["Key", "Value"])
        self.tab_ad_meta_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tab_ad_meta_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.tab_ad_meta_table.setStyleSheet("font-family: 'Courier New', monospace;")

        layout_tab_ad_meta = QVBoxLayout()
        layout_tab_ad_meta.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_tab_ad_meta.addWidget(self.tab_ad_meta_table)
        self.tab_ad_meta.setLayout(layout_tab_ad_meta)

        # BOX - Tab Tree 
        self.tab_sd_tree_str = QListWidget()
        self.tab_sd_tree_str.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.tab_sd_tree_str.setStyleSheet("font-family: 'Courier New', monospace;")

        layout_tab_sd_tree = QVBoxLayout()
        layout_tab_sd_tree.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_tab_sd_tree.addWidget(self.tab_sd_tree_str)
        self.tab_sd_tree.setLayout(layout_tab_sd_tree)

        self.tab_ad_tree_str = QListWidget()
        self.tab_ad_tree_str.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.tab_ad_tree_str.setStyleSheet("font-family: 'Courier New', monospace;")

        layout_tab_ad_tree = QVBoxLayout()
        layout_tab_ad_tree.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_tab_ad_tree.addWidget(self.tab_ad_tree_str)
        self.tab_ad_tree.setLayout(layout_tab_ad_tree)

        ###### TAB - ALL ######
        self.tabs.addTab(self.tabs_sd, "Data tabulation")
        self.tabs_sd.addTab(self.tab_sd_meta, "Meta")
        self.tabs_sd.addTab(self.tab_sd_tree, "Tree")
        self.tabs.addTab(self.tabs_ad, "Analysis datasets")
        self.tabs_ad.addTab(self.tab_ad_meta, "Meta")
        self.tabs_ad.addTab(self.tab_ad_tree, "Tree")

        # BOX - Message List Widget
        self.message_list = QListWidget()
        self.message_list.setFixedHeight(self.message_list.sizeHintForRow(0) + 70)
        self.message_list.setStyleSheet("background-color: rgba(80, 80, 80, 0.15);")

        layout_tab = QVBoxLayout()
        layout_tab.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_tab.addLayout(layout_button)
        layout_tab.addWidget(self.tabs)
        layout_tab.addWidget(self.message_list)
        self.setLayout(layout_tab)

    @staticmethod
    def util_get_folder_meta_info(folder):
        folder_size = sum(
            os.path.getsize(os.path.join(dirpath, filename))
            for dirpath, _, filenames in os.walk(folder)
            for filename in filenames
        )
        folder_ctime = datetime.fromtimestamp(os.path.getctime(folder))
        folder_mtime = datetime.fromtimestamp(os.path.getmtime(folder))
        now = datetime.now()
        meta_info = {
            "folder_path": folder,
            "folder_size": folder_size,
            "created": folder_ctime.strftime('%Y-%m-%d %H:%M:%S'),
            "modified": folder_mtime.strftime('%Y-%m-%d %H:%M:%S'),
            "scan_time": now.strftime('%Y-%m-%d %H:%M:%S'),
            "user": os.getlogin(),
            "mtbp3cd_version": getattr(__import__("mtbp3cd"), "__version__", "unknown")
        }
        return meta_info

    def tab_button_1_f(self):
        folder = QFileDialog.getExistingDirectory(self, "Data tabulation")
        if folder:
            if not os.path.exists(folder):
                mtbp3cd.gui.util_show_message(self.message_list, f"Selected data tabulation folder does not exist: {folder}", status="f")
                return
            mtbp3cd.gui.util_show_message(self.message_list, f"Selected data tabulation folder: {folder}", status="s")
            self.tab_sd_path = folder
            self.tab_sd_meta_json = self.util_get_folder_meta_info(folder)
            self.tab_sd_meta_table.setRowCount(len(self.tab_sd_meta_json))
            for row, (key, value) in enumerate(self.tab_sd_meta_json.items()):
                key_item = QTableWidgetItem(str(key))
                value_item = QTableWidgetItem(str(value))
                self.tab_sd_meta_table.setItem(row, 0, key_item)
                self.tab_sd_meta_table.setItem(row, 1, value_item)
            self.tab_sd_meta_table.resizeColumnsToContents()
            lsr1 = LsrTree(folder, outfmt="tree", with_counts=True)
            self.tab_sd_tree_str0 = lsr1.list_files() 
            width = len(str(len(self.tab_sd_tree_str0)))
            self.tab_sd_tree_str.addItems([f"{str(idx+1).rjust(width, ' ')}: {str(item)}" for idx, item in enumerate(self.tab_sd_tree_str0)])
            lsr2 = LsrTree(folder, outfmt="dataframe")
            self.tab_sd_df = lsr2.list_files_dataframe()
            self.tabs.setCurrentWidget(self.tabs_sd)

    def tab_button_2_f(self):
        folder = QFileDialog.getExistingDirectory(self, "Analysis datasets")
        if folder:
            if not os.path.exists(folder):
                mtbp3cd.gui.util_show_message(self.message_list, f"Selected analysis datasets folder does not exist: {folder}", status="f")
                return
            mtbp3cd.gui.util_show_message(self.message_list, f"Selected analysis datasets folder: {folder}", status="s")
            self.tab_ad_path = folder
            self.tab_ad_meta_json = self.util_get_folder_meta_info(folder)
            self.tab_ad_meta_table.setRowCount(len(self.tab_ad_meta_json))
            for row, (key, value) in enumerate(self.tab_ad_meta_json.items()):
                key_item = QTableWidgetItem(str(key))
                value_item = QTableWidgetItem(str(value))
                self.tab_ad_meta_table.setItem(row, 0, key_item)
                self.tab_ad_meta_table.setItem(row, 1, value_item)
            self.tab_ad_meta_table.resizeColumnsToContents()
            lsr1 = LsrTree(folder, outfmt="tree", with_counts=True)
            self.tab_ad_tree_str0 = lsr1.list_files() 
            self.tab_ad_tree_str.clear()
            width = len(str(len(self.tab_ad_tree_str0)))
            self.tab_ad_tree_str.addItems([f"{str(idx+1).rjust(width, ' ')}: {str(item)}" for idx, item in enumerate(self.tab_ad_tree_str0)])
            lsr2 = LsrTree(folder, outfmt="dataframe")
            self.tab_ad_df = lsr2.list_files_dataframe()

            self.tabs.setCurrentWidget(self.tabs_ad)

    def tab_button_3_f(self):
        file_path_base = getattr(self._p.tab_starting, "gt01_output_folder_path", None)
        if not file_path_base:
            mtbp3cd.gui.util_show_message(self.message_list, "Please select output folder in the previous step", status="i")
            return

        log_sd_path = os.path.join(file_path_base, "log_sdtm")
        if os.path.exists(log_sd_path) and os.listdir(log_sd_path):
            mtbp3cd.gui.util_show_message(self.message_list, f"Warning: log_sdtm folder is not empty and will be overwritten.", status="i")
        else:
            os.makedirs(log_sd_path, exist_ok=True)
        log_ad_path = os.path.join(file_path_base, "log_adam")
        if os.path.exists(log_ad_path) and os.listdir(log_ad_path):
            mtbp3cd.gui.util_show_message(self.message_list, f"Warning: log_adam folder is not empty and will be overwritten.", status="i")
        else:
            os.makedirs(log_ad_path, exist_ok=True)

        if hasattr(self, "tab_sd_tree_str0"):
            file_path = os.path.join(log_sd_path, "log_folder_tree.txt")
            if self.tab_sd_tree_str0.empty or len(self.tab_sd_tree_str0) == 0:
                mtbp3cd.gui.util_show_message(self.message_list, "No tabulation folder tree to export.", status="i")
            else:
                try:
                    with open(file_path, "w", encoding="utf-8") as f:
                        for item in self.tab_sd_tree_str0:
                            f.write(str(item) + "\n")
                    mtbp3cd.gui.util_show_message(self.message_list, f"Tree exported (sdtm): {file_path}", status="s")
                except Exception as e:
                    mtbp3cd.gui.util_show_message(self.message_list, f"Failed to export (sdtm): {e}", status="f")

        if hasattr(self, "tab_sd_meta_json"):
            meta_json_path = os.path.join(log_sd_path, "log_folder_meta.json")
            if not self.tab_sd_meta_json or len(self.tab_sd_meta_json) == 0:
                mtbp3cd.gui.util_show_message(self.message_list, "No tabulation folder meta to export.", status="i")
            else:
                try:
                    with open(meta_json_path, "w", encoding="utf-8") as f:
                        json.dump(self.tab_sd_meta_json, f, indent=2)
                    mtbp3cd.gui.util_show_message(self.message_list, f"Meta exported (sdtm): {meta_json_path}", status="s")
                except Exception as e:
                    mtbp3cd.gui.util_show_message(self.message_list, f"Failed to export meta.json (sdtm): {e}", status="f")

        if hasattr(self, "tab_sd_df"):
            file_path = os.path.join(log_sd_path, "log_folder_table.csv")
            if not hasattr(self, "tab_sd_df") or self.tab_sd_df is None or self.tab_sd_df.empty:
                mtbp3cd.gui.util_show_message(self.message_list, "No tabulation folder dataframe to export.", status="i")
            else:
                try:
                    self.tab_sd_df.to_csv(file_path, index=False)
                    mtbp3cd.gui.util_show_message(self.message_list, f"CSV exported (sdtm): {file_path}", status="s")
                except Exception as e:
                    mtbp3cd.gui.util_show_message(self.message_list, f"Failed to export CSV (sdtm): {e}", status="f")

        if hasattr(self, "tab_ad_tree_str0"):
            file_path = os.path.join(log_ad_path, "log_folder_tree.txt")
            if self.tab_ad_tree_str0.empty or len(self.tab_ad_tree_str0) == 0:
                mtbp3cd.gui.util_show_message(self.message_list, "No analysis folder tree to export.", status="i")
            else:
                try:
                    with open(file_path, "w", encoding="utf-8") as f:
                        for item in self.tab_ad_tree_str0:
                            f.write(str(item) + "\n")
                    mtbp3cd.gui.util_show_message(self.message_list, f"Tree exported (adam): {file_path}", status="s")
                except Exception as e:
                    mtbp3cd.gui.util_show_message(self.message_list, f"Failed to export (adam): {e}", status="f")

        if hasattr(self, "tab_ad_meta_json"):
            meta_json_path = os.path.join(log_ad_path, "log_folder_meta.json")
            if not self.tab_ad_meta_json or len(self.tab_ad_meta_json) == 0:
                mtbp3cd.gui.util_show_message(self.message_list, "No analysis folder meta to export.", status="i")
            else:
                try:
                    with open(meta_json_path, "w", encoding="utf-8") as f:
                        json.dump(self.tab_ad_meta_json, f, indent=2)
                    mtbp3cd.gui.util_show_message(self.message_list, f"Meta exported (adam): {meta_json_path}", status="s")
                except Exception as e:
                    mtbp3cd.gui.util_show_message(self.message_list, f"Failed to export meta.json (adam): {e}", status="f")

        if hasattr(self, "tab_ad_df"):
            file_path = os.path.join(log_ad_path, "log_folder_table.csv")
            if not hasattr(self, "tab_ad_df") or self.tab_ad_df is None or self.tab_ad_df.empty:
                mtbp3cd.gui.util_show_message(self.message_list, "No analysis folder dataframe to export.", status="i")
            else:
                try:
                    self.tab_ad_df.to_csv(file_path, index=False)
                    mtbp3cd.gui.util_show_message(self.message_list, f"CSV exported (adam): {file_path}", status="s")
                except Exception as e:
                    mtbp3cd.gui.util_show_message(self.message_list, f"Failed to export CSV (adam): {e}", status="f")

if __name__ == "__main__":
    pass