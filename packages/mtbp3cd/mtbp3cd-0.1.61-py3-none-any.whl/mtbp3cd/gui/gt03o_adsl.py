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
import glob
import re
import xml.etree.ElementTree as ET

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, 
    QPushButton, QLabel,
    QTableWidget, QFileDialog,
    QTabWidget, QHBoxLayout,
    QTableWidgetItem, QListWidget
)

class TabADSL(QWidget):
    def __init__(self, _p):
        super().__init__()
        self._p = _p

        self.tab_button_1 = QPushButton("Find adsl")
        self.tab_button_1.setEnabled(True)
        self.tab_button_1.clicked.connect(self.tab_button_1_f)

        self.tab_button_2 = QPushButton("Find adae")
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
        self.tab_sd_meta_table.setHorizontalHeaderLabels(["Key", "Value", "key_ns"])
        self.tab_sd_meta_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tab_sd_meta_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.tab_sd_meta_table.setStyleSheet("font-family: 'Courier New', monospace;")

        layout_tab_sd_meta = QVBoxLayout()
        layout_tab_sd_meta.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_tab_sd_meta.addWidget(self.tab_sd_meta_table)
        self.tab_sd_meta.setLayout(layout_tab_sd_meta)

        self.tab_ad_meta_table = QTableWidget()
        self.tab_ad_meta_table.setColumnCount(2)
        self.tab_ad_meta_table.setHorizontalHeaderLabels(["Key", "Value", "key_ns"])
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
        self.tabs_ad.addTab(self.tab_ad_tree, "MDV")

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
    def util_get_define_meta_info(folder):
        pass

    def tab_button_1_f(self):
        pass
    def tab_button_3_f(self):
        pass

    def tab_button_2_f(self):
        folder = None
        tab_ad_path = getattr(getattr(self._p, "tab_input", None), "tab_ad_path", None)
        if tab_ad_path and os.path.isdir(tab_ad_path):
            folder = tab_ad_path
        else:
            folder = QFileDialog.getExistingDirectory(self, "Select Analysis define.xml Folder")
        if not folder:
            return

        if folder:
            self.sd_folder_path = folder
            self.tab_sd_meta_df = self.util_get_define_meta_info(folder)

            self.tab_ad_meta_table.setRowCount(0)
            for row_idx, row in self.tab_sd_meta_df.iterrows():
                key_item = QTableWidgetItem(str(row["key"]))
                value_item = QTableWidgetItem(str(row["value"]))
                self.tab_ad_meta_table.insertRow(row_idx)
                self.tab_ad_meta_table.setItem(row_idx, 0, key_item)
                self.tab_ad_meta_table.setItem(row_idx, 1, value_item)
            self.tab_ad_meta_table.resizeColumnsToContents()


if __name__ == "__main__":
    pass