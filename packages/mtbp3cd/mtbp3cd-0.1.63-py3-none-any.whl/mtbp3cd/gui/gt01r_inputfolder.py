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

class TabFolder(QWidget):
    def __init__(self, _p):
        super().__init__()
        self._p = _p

        self.tab_button_1 = QPushButton("Step 1: Select Folder")
        self.tab_button_1.setEnabled(True)
        self.tab_button_1.clicked.connect(self.tab_button_1_f)

        self.tab_button_2 = QPushButton("Step 2: Save tree.txt, meta.json, and table.csv")
        self.tab_button_2.setEnabled(False)
        self.tab_button_2.clicked.connect(self.tab_button_2_f)

        layout_button = QHBoxLayout()
        layout_button.addWidget(self.tab_button_1)
        layout_button.addWidget(self.tab_button_2)

        # BOX - tabs
        self.tabs = QTabWidget()
        self.tab_meta = QWidget()
        self.tab_tree = QWidget()
        self.tab_table = QWidget()
        self.tab_list = QWidget()

        # BOX - Tab Meta 
        self.tab_meta_table = QTableWidget()
        self.tab_meta_table.setColumnCount(2)
        self.tab_meta_table.setHorizontalHeaderLabels(["Key", "Value"])
        self.tab_meta_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tab_meta_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.tab_meta_table.setStyleSheet("font-family: 'Courier New', monospace;")

        layout_tab_meta = QVBoxLayout()
        layout_tab_meta.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_tab_meta.addWidget(self.tab_meta_table)
        self.tab_meta.setLayout(layout_tab_meta)

        # BOX - Tab Tree 
        self.tab_tree_str = QListWidget()
        self.tab_tree_str.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.tab_tree_str.setStyleSheet("font-family: 'Courier New', monospace;")

        layout_tab_tree = QVBoxLayout()
        layout_tab_tree.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_tab_tree.addWidget(self.tab_tree_str)
        self.tab_tree.setLayout(layout_tab_tree)

        # BOX - DataFrame Preview 
        self.tab_table_qttable = QTableWidget()
        self.tab_table_qttable.setColumnCount(0)
        self.tab_table_qttable.setRowCount(0)
        self.tab_table_qttable.setVisible(True)

        layout_tab_table = QVBoxLayout()
        layout_tab_table.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_tab_table.addWidget(self.tab_table_qttable)
        self.tab_table.setLayout(layout_tab_table)

        # BOX - Tab List 
        self.tab_list_str = QListWidget()
        self.tab_list_str.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.tab_list_str.setStyleSheet("font-family: 'Courier New', monospace;")

        layout_tab_list = QVBoxLayout()
        layout_tab_list.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_tab_list.addWidget(self.tab_list_str)
        self.tab_list.setLayout(layout_tab_list)

        ###### TAB - ALL ######
        self.tabs.addTab(self.tab_meta, "Meta")
        self.tabs.addTab(self.tab_tree, "Tree")
        self.tabs.addTab(self.tab_table, "Table")
        self.tabs.addTab(self.tab_list, "List")

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

    # def show_message(self, message, status="info"):
    #     color_map = {
    #         "success": Qt.GlobalColor.green,
    #         "fail": Qt.GlobalColor.red,
    #         "info": Qt.GlobalColor.blue
    #     }
    #     color = color_map.get(status, Qt.GlobalColor.black)
    #     self.message_list.addItem(message)
    #     self.message_list.item(self.message_list.count() - 1).setForeground(color)
    #     self.message_list.scrollToBottom()

    def tab_button_1_f(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.gt01_input_folder_path = folder
            self.tab_folder_meta_json = self.util_get_folder_meta_info(folder)
            self.tab_meta_table.setRowCount(len(self.tab_folder_meta_json))
            for row, (key, value) in enumerate(self.tab_folder_meta_json.items()):
                key_item = QTableWidgetItem(str(key))
                value_item = QTableWidgetItem(str(value))
                self.tab_meta_table.setItem(row, 0, key_item)
                self.tab_meta_table.setItem(row, 1, value_item)
            self.tab_meta_table.resizeColumnsToContents()
            lsr1 = LsrTree(folder, outfmt="tree", with_counts=True)
            self.tab_folder_tree_str = lsr1.list_files() 
            self.tab_button_2.setEnabled(bool(len(self.tab_folder_tree_str)>0))
            self.tab_tree_str.clear()
            width = len(str(len(self.tab_folder_tree_str)))
            self.tab_tree_str.addItems([f"{str(idx+1).zfill(width)}: {str(item)}" for idx, item in enumerate(self.tab_folder_tree_str)])
            lsr2 = LsrTree(folder, outfmt="dataframe")
            self.folder_file_list = lsr2.list_files_list()
            self.folder_file_df = lsr2.list_files_dataframe()
            self.tab_list_str.clear()
            self.tab_list_str.addItems([f"{str(idx+1).zfill(width)}: {str(item)}" for idx, item in enumerate(self.folder_file_list)])

            # Display DataFrame in the QTableWidget
            self.tab_table_qttable.clear()
            self.tab_table_qttable.setRowCount(self.folder_file_df.shape[0])
            self.tab_table_qttable.setColumnCount(self.folder_file_df.shape[1])
            self.tab_table_qttable.setHorizontalHeaderLabels([str(col) for col in self.folder_file_df.columns])

            for row in range(self.folder_file_df.shape[0]):
                for col in range(self.folder_file_df.shape[1]-1):
                    value = str(self.folder_file_df.iat[row, col])
                    item = QTableWidgetItem(value)
                    self.tab_table_qttable.setItem(row, col, item)
            self.tab_table_qttable.resizeColumnsToContents()

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

    def tab_button_2_f(self):
        file_path_base = getattr(self._p.tab_starting, "gt01_output_folder_path", None)
        if not file_path_base:
            mtbp3cd.gui.util_show_message(self.message_list, "Please select output folder in the previous step", status="success")
            return
        file_path = os.path.join(file_path_base, "log_folder_tree.txt")
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                for item in self.tab_folder_tree_str:
                    f.write(str(item) + "\n")
            mtbp3cd.gui.util_show_message(self.message_list, f"Tree exported: {file_path}", status="s")
        except Exception as e:
            mtbp3cd.gui.util_show_message(self.message_list, f"Failed to export: {e}", status="f")

        meta_json_path = os.path.join(file_path_base, "log_folder_meta.json")
        try:
            with open(meta_json_path, "w", encoding="utf-8") as f:
                json.dump(self.tab_folder_meta_json, f, indent=2)
            mtbp3cd.gui.util_show_message(self.message_list, f"Meta exported: {meta_json_path}", status="s")
        except Exception as e:
            mtbp3cd.gui.util_show_message(self.message_list, f"Failed to export meta.json: {e}", status="f")

        file_path = os.path.join(file_path_base, "log_folder_table.csv")
        try:
            self.folder_file_df.to_csv(file_path, index=False)
            mtbp3cd.gui.util_show_message(self.message_list, f"CSV exported: {file_path}", status="s")
        except Exception as e:
            mtbp3cd.gui.util_show_message(self.message_list, f"Failed to export CSV: {e}", status="f")


if __name__ == "__main__":
    pass