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
import mtbp3cd.gui

import json
import glob
import re
from mtbp3cd.util.gt03define import DefineXML
import xml.etree.ElementTree as ET

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, 
    QPushButton, QLabel,
    QTableWidget, QFileDialog,
    QTabWidget, QHBoxLayout,
    QTableWidgetItem, QListWidget
)

class DefaultTableWidget(QTableWidget):
    def __init__(self, column_titles, parent=None):
        super().__init__(parent)
        self.setColumnCount(len(column_titles))
        self.setHorizontalHeaderLabels(column_titles)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.setStyleSheet("font-family: 'Courier New', monospace;")

class TabDefine(QWidget):
    def __init__(self, _p):
        super().__init__()
        self._p = _p

        self.tab_button_1 = QPushButton("Find Tabulation define.xml")
        self.tab_button_1.setEnabled(True)
        self.tab_button_1.clicked.connect(self.tab_button_1_f)

        self.tab_button_2 = QPushButton("Find Analysis define.xml")
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
        self.tab_sd_igdef = QWidget()
        self.tab_sd_desc = QWidget()
        self.tab_sd_descf = QWidget()

        self.tab_ad_meta = QWidget()
        self.tab_ad_igdef = QWidget()
        self.tab_ad_desc = QWidget()
        self.tab_ad_descf = QWidget()

        # BOX - Tab Meta 
        self.tab_sd_meta_table = DefaultTableWidget(["Key", "Value", "ns"])
        layout_tab_sd_meta = QVBoxLayout()
        layout_tab_sd_meta.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_tab_sd_meta.addWidget(self.tab_sd_meta_table)
        self.tab_sd_meta.setLayout(layout_tab_sd_meta)

        self.tab_ad_meta_table = DefaultTableWidget(["Key", "Value", "ns"])
        layout_tab_ad_meta = QVBoxLayout()
        layout_tab_ad_meta.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_tab_ad_meta.addWidget(self.tab_ad_meta_table)
        self.tab_ad_meta.setLayout(layout_tab_ad_meta)

        # BOX - Tab igdef 
        self.tab_sd_igdef_table = DefaultTableWidget(["Id", "File Name", "Description"])
        layout_tab_sd_igdef = QVBoxLayout()
        layout_tab_sd_igdef.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_tab_sd_igdef.addWidget(self.tab_sd_igdef_table)
        self.tab_sd_igdef.setLayout(layout_tab_sd_igdef)

        self.tab_ad_igdef_table = DefaultTableWidget(["Id", "File Name", "Description"])
        layout_tab_ad_igdef = QVBoxLayout()
        layout_tab_ad_igdef.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_tab_ad_igdef.addWidget(self.tab_ad_igdef_table)
        self.tab_ad_igdef.setLayout(layout_tab_ad_igdef)

        # BOX - Tab desc 
        self.tab_sd_desc_table = DefaultTableWidget(["Domain", "Column_value", "Type", "Length", "Description", "CL_OID", "Flag", "AVAL"])
        layout_tab_sd_desc = QVBoxLayout()
        layout_tab_sd_desc.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_tab_sd_desc.addWidget(self.tab_sd_desc_table)
        self.tab_sd_desc.setLayout(layout_tab_sd_desc)

        self.tab_ad_desc_table = DefaultTableWidget(["Domain", "Column_value", "Type", "Length", "Description", "CL_OID", "Flag", "AVAL"])
        layout_tab_ad_desc = QVBoxLayout()
        layout_tab_ad_desc.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_tab_ad_desc.addWidget(self.tab_ad_desc_table)
        self.tab_ad_desc.setLayout(layout_tab_ad_desc)

        # BOX - Tab desc Flag
        self.tab_sd_descf_table = DefaultTableWidget(["Domain", "Column_value", "Type", "Length", "Description", "CL_OID", "Flag", "AVAL"])
        layout_tab_sd_descf = QVBoxLayout()
        layout_tab_sd_descf.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_tab_sd_descf.addWidget(self.tab_sd_descf_table)
        self.tab_sd_descf.setLayout(layout_tab_sd_descf)

        self.tab_ad_descf_table = DefaultTableWidget(["Domain", "Column_value", "Type", "Length", "Description", "CL_OID", "Flag", "AVAL"])
        layout_tab_ad_descf = QVBoxLayout()
        layout_tab_ad_descf.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_tab_ad_descf.addWidget(self.tab_ad_descf_table)
        self.tab_ad_descf.setLayout(layout_tab_ad_descf)

        ###### TAB - ALL ######
        self.tabs.addTab(self.tabs_sd, "Data tabulation")
        self.tabs_sd.addTab(self.tab_sd_meta, "Meta")
        self.tabs_sd.addTab(self.tab_sd_igdef, "File")
        self.tabs_sd.addTab(self.tab_sd_desc, "Col. Description")
        self.tabs_sd.addTab(self.tab_sd_descf, "Flag")
        self.tabs.addTab(self.tabs_ad, "Analysis datasets")
        self.tabs_ad.addTab(self.tab_ad_meta, "Meta")
        self.tabs_ad.addTab(self.tab_ad_igdef, "File")
        self.tabs_ad.addTab(self.tab_ad_desc, "Col. Description")
        self.tabs_ad.addTab(self.tab_ad_descf, "Flag")

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

    def tab_button_1_f(self):
        folder = None
        tab_sd_path = getattr(getattr(self._p, "tab_input", None), "tab_sd_path", None)
        if tab_sd_path and os.path.isdir(tab_sd_path):
            folder = tab_sd_path
        else:
            folder = QFileDialog.getExistingDirectory(self, "Select Analysis define.xml Folder")
        if not folder:
            return
        self.tabs.setCurrentWidget(self.tabs_ad)

        if folder:
            self.sd_folder_path = folder
            for f in os.listdir(folder):
                if f.lower() == "define.xml":
                    xml_file = os.path.join(folder, f)
                    break

            dx = DefineXML()
            result = dx.read(xml_file)

            self.tab_sd_meta_df=pd.DataFrame(result["meta"], columns=["key", "value", "ns"])
            self.tab_sd_igdef_df=pd.DataFrame(result["ig_desc"], columns=["key", "value", "description"])
            self.tab_sd_igdef_oid=result["ig_structure"]
            self.tab_sd_igdef_oid_desc=pd.DataFrame(result["ig_it_desc"], columns=["idx","domain","column","type", "length", "description", "cloid","flag","aval"])

            self.tab_sd_meta_table.setRowCount(0)
            for row_idx, row in self.tab_sd_meta_df.iterrows():
                item1 = QTableWidgetItem(str(row["key"]))
                item2 = QTableWidgetItem(str(row["value"]))
                self.tab_sd_meta_table.insertRow(row_idx)
                self.tab_sd_meta_table.setItem(row_idx, 0, item1)
                self.tab_sd_meta_table.setItem(row_idx, 1, item2)
            self.tab_sd_meta_table.resizeColumnsToContents()

            self.tab_sd_igdef_table.setRowCount(0)
            for row_idx, row in self.tab_sd_igdef_df.iterrows():
                item1 = QTableWidgetItem(str(row["key"]))
                item2 = QTableWidgetItem(str(row["value"]))
                item3 = QTableWidgetItem(str(row["description"]))
                self.tab_sd_igdef_table.insertRow(row_idx)
                self.tab_sd_igdef_table.setItem(row_idx, 0, item1)
                self.tab_sd_igdef_table.setItem(row_idx, 1, item2)
                self.tab_sd_igdef_table.setItem(row_idx, 2, item3)
            self.tab_sd_igdef_table.resizeColumnsToContents()

            self.tab_sd_desc_table.setRowCount(0)
            for row_idx, row in self.tab_sd_igdef_oid_desc.iterrows():
                item0 = QTableWidgetItem(str(row["domain"]))
                item1 = QTableWidgetItem(str(row["column"]))
                item2 = QTableWidgetItem(str(row["type"]))
                item3 = QTableWidgetItem(str(row["length"]))
                item4 = QTableWidgetItem(str(row["description"]))
                item5 = QTableWidgetItem(str(row["cloid"]))
                item6 = QTableWidgetItem(str(row["flag"]))
                item7 = QTableWidgetItem(str(row["aval"]))
                self.tab_sd_desc_table.insertRow(row_idx)
                self.tab_sd_desc_table.setItem(row_idx, 0, item0)
                self.tab_sd_desc_table.setItem(row_idx, 1, item1)
                self.tab_sd_desc_table.setItem(row_idx, 2, item2)
                self.tab_sd_desc_table.setItem(row_idx, 3, item3)
                self.tab_sd_desc_table.setItem(row_idx, 4, item4)
                self.tab_sd_desc_table.setItem(row_idx, 5, item5)
                self.tab_sd_desc_table.setItem(row_idx, 6, item6)
                self.tab_sd_desc_table.setItem(row_idx, 7, item7)
            self.tab_sd_desc_table.resizeColumnsToContents()

            self.tab_sd_flag_df = self.tab_sd_igdef_oid_desc[self.tab_sd_igdef_oid_desc["flag"]]

            self.tab_sd_descf_table.setRowCount(0)
            for row_idx, row in self.tab_sd_flag_df.iterrows():
                item0 = QTableWidgetItem(str(row["domain"]))
                item1 = QTableWidgetItem(str(row["column"]))
                item2 = QTableWidgetItem(str(row["type"]))
                item3 = QTableWidgetItem(str(row["length"]))
                item4 = QTableWidgetItem(str(row["description"]))
                item5 = QTableWidgetItem(str(row["cloid"]))
                item6 = QTableWidgetItem(str(row["flag"]))
                item7 = QTableWidgetItem(str(row["aval"]))
                self.tab_sd_descf_table.insertRow(row_idx)
                self.tab_sd_descf_table.setItem(row_idx, 0, item0)
                self.tab_sd_descf_table.setItem(row_idx, 1, item1)
                self.tab_sd_descf_table.setItem(row_idx, 2, item2)
                self.tab_sd_descf_table.setItem(row_idx, 3, item3)
                self.tab_sd_descf_table.setItem(row_idx, 4, item4)
                self.tab_sd_descf_table.setItem(row_idx, 5, item5)
                self.tab_sd_descf_table.setItem(row_idx, 6, item6)
                self.tab_sd_descf_table.setItem(row_idx, 7, item7)
            self.tab_sd_descf_table.resizeColumnsToContents()

    def tab_button_2_f(self):
        folder = None
        tab_ad_path = getattr(getattr(self._p, "tab_input", None), "tab_ad_path", None)
        if tab_ad_path and os.path.isdir(tab_ad_path):
            folder = tab_ad_path
        else:
            folder = QFileDialog.getExistingDirectory(self, "Select Analysis define.xml Folder")
        if not folder:
            return
        self.tabs.setCurrentWidget(self.tabs_ad)

        if folder:
            self.ad_folder_path = folder
            for f in os.listdir(folder):
                if f.lower() == "define.xml":
                    xml_file = os.path.join(folder, f)
                    break

            dx = DefineXML()
            result = dx.read(xml_file)

            self.tab_ad_meta_df=pd.DataFrame(result["meta"], columns=["key", "value", "ns"])
            self.tab_ad_igdef_df=pd.DataFrame(result["ig_desc"], columns=["key", "value", "description"])
            self.tab_ad_igdef_oid=result["ig_structure"]
            self.tab_ad_igdef_oid_desc=pd.DataFrame(result["ig_it_desc"], columns=["idx", "domain", "column","type", "length", "description", "cloid","flag","aval"])

            self.tab_ad_meta_table.setRowCount(0)
            for row_idx, row in self.tab_ad_meta_df.iterrows():
                item1 = QTableWidgetItem(str(row["key"]))
                item2 = QTableWidgetItem(str(row["value"]))
                self.tab_ad_meta_table.insertRow(row_idx)
                self.tab_ad_meta_table.setItem(row_idx, 0, item1)
                self.tab_ad_meta_table.setItem(row_idx, 1, item2)
            self.tab_ad_meta_table.resizeColumnsToContents()

            self.tab_ad_igdef_table.setRowCount(0)
            for row_idx, row in self.tab_ad_igdef_df.iterrows():
                item1 = QTableWidgetItem(str(row["key"]))
                item2 = QTableWidgetItem(str(row["value"]))
                item3 = QTableWidgetItem(str(row["description"]))
                self.tab_ad_igdef_table.insertRow(row_idx)
                self.tab_ad_igdef_table.setItem(row_idx, 0, item1)
                self.tab_ad_igdef_table.setItem(row_idx, 1, item2)
                self.tab_ad_igdef_table.setItem(row_idx, 2, item3)
            self.tab_ad_igdef_table.resizeColumnsToContents()

            self.tab_ad_desc_table.setRowCount(0)
            for row_idx, row in self.tab_ad_igdef_oid_desc.iterrows():
                item0 = QTableWidgetItem(str(row["domain"]))
                item1 = QTableWidgetItem(str(row["column"]))
                item2 = QTableWidgetItem(str(row["type"]))
                item3 = QTableWidgetItem(str(row["length"]))
                item4 = QTableWidgetItem(str(row["description"]))
                item5 = QTableWidgetItem(str(row["cloid"]))
                item6 = QTableWidgetItem(str(row["flag"]))
                item7 = QTableWidgetItem(str(row["aval"]))
                self.tab_ad_desc_table.insertRow(row_idx)
                self.tab_ad_desc_table.setItem(row_idx, 0, item0)
                self.tab_ad_desc_table.setItem(row_idx, 1, item1)
                self.tab_ad_desc_table.setItem(row_idx, 2, item2)
                self.tab_ad_desc_table.setItem(row_idx, 3, item3)
                self.tab_ad_desc_table.setItem(row_idx, 4, item4)
                self.tab_ad_desc_table.setItem(row_idx, 5, item5)
                self.tab_ad_desc_table.setItem(row_idx, 6, item6)
                self.tab_ad_desc_table.setItem(row_idx, 7, item7)
            self.tab_ad_desc_table.resizeColumnsToContents()

            self.tab_ad_flag_df = self.tab_ad_igdef_oid_desc[self.tab_ad_igdef_oid_desc["flag"]]

            self.tab_ad_descf_table.setRowCount(0)
            for row_idx, row in self.tab_ad_flag_df.iterrows():
                item0 = QTableWidgetItem(str(row["domain"]))
                item1 = QTableWidgetItem(str(row["column"]))
                item2 = QTableWidgetItem(str(row["type"]))
                item3 = QTableWidgetItem(str(row["length"]))
                item4 = QTableWidgetItem(str(row["description"]))
                item5 = QTableWidgetItem(str(row["cloid"]))
                item6 = QTableWidgetItem(str(row["flag"]))
                item7 = QTableWidgetItem(str(row["aval"]))
                self.tab_ad_descf_table.insertRow(row_idx)
                self.tab_ad_descf_table.setItem(row_idx, 0, item0)
                self.tab_ad_descf_table.setItem(row_idx, 1, item1)
                self.tab_ad_descf_table.setItem(row_idx, 2, item2)
                self.tab_ad_descf_table.setItem(row_idx, 3, item3)
                self.tab_ad_descf_table.setItem(row_idx, 4, item4)
                self.tab_ad_descf_table.setItem(row_idx, 5, item5)
                self.tab_ad_descf_table.setItem(row_idx, 6, item6)
                self.tab_ad_descf_table.setItem(row_idx, 7, item7)
            self.tab_ad_descf_table.resizeColumnsToContents()


    def tab_button_3_f(self):
        file_path_base = getattr(self._p.tab_starting, "gt01_output_folder_path", None)
        if not file_path_base:
            mtbp3cd.gui.util_show_message(self.message_list, "Please select output folder in the previous step", status="success")
            return
        log_folder = os.path.join(file_path_base, "log_define_xml")
        
        if os.path.exists(log_folder) and os.listdir(log_folder):
            mtbp3cd.gui.util_show_message(self.message_list, f"Warning: log folder '{log_folder}' exists and is not empty. Files may be overwritten.", status="i")
        try:
            os.makedirs(log_folder, exist_ok=True)
        except Exception as e:
            mtbp3cd.gui.util_show_message(self.message_list, f"Failed to create log folder: {e}", status="f")
            return
        file_path_base = log_folder

        # Save tab_sd_meta_df
        file_path = os.path.join(file_path_base, "log_sd_meta.csv")
        try:
            self.tab_sd_meta_df.to_csv(file_path, index=False)
            mtbp3cd.gui.util_show_message(self.message_list, f"sd_meta_df saved: {file_path}", status="s")
        except Exception as e:
            mtbp3cd.gui.util_show_message(self.message_list, f"Failed to export tab_sd_meta_df: {e}", status="f")

        # Save tab_sd_igdef_df
        file_path = os.path.join(file_path_base, "log_sd_ig.csv")
        try:
            self.tab_sd_igdef_df.to_csv(file_path, index=False)
            mtbp3cd.gui.util_show_message(self.message_list, f"sd_igdef_df saved: {file_path}", status="s")
        except Exception as e:
            mtbp3cd.gui.util_show_message(self.message_list, f"Failed to export tab_sd_igdef_df: {e}", status="f")

        # Save tab_sd_igdef_oid_desc
        file_path = os.path.join(file_path_base, "log_sd_it.csv")
        try:
            self.tab_sd_igdef_oid_desc.to_csv(file_path, index=False)
            mtbp3cd.gui.util_show_message(self.message_list, f"sd_igdef_oid_desc saved: {file_path}", status="s")
        except Exception as e:
            mtbp3cd.gui.util_show_message(self.message_list, f"Failed to export sd_igdef_oid_desc: {e}", status="f")

        file_path = os.path.join(file_path_base, "log_sd_ig_it_flag.csv")
        try:
            self.tab_sd_flag_df.to_csv(file_path, index=False)
            mtbp3cd.gui.util_show_message(self.message_list, f"ad_igdef_oid_desc saved: {file_path}", status="s")
        except Exception as e:
            mtbp3cd.gui.util_show_message(self.message_list, f"Failed to export ad_igdef_oid_desc: {e}", status="f")

        # Save tab_ad_meta_df
        file_path = os.path.join(file_path_base, "log_ad_meta.csv")
        try:
            self.tab_ad_meta_df.to_csv(file_path, index=False)
            mtbp3cd.gui.util_show_message(self.message_list, f"ad_meta_df saved: {file_path}", status="s")
        except Exception as e:
            mtbp3cd.gui.util_show_message(self.message_list, f"Failed to export tab_ad_meta_df: {e}", status="f")

        # Save tab_ad_igdef_df
        file_path = os.path.join(file_path_base, "log_ad_ig.csv")
        try:
            self.tab_ad_igdef_df.to_csv(file_path, index=False)
            mtbp3cd.gui.util_show_message(self.message_list, f"ad_igdef_df saved: {file_path}", status="s")
        except Exception as e:
            mtbp3cd.gui.util_show_message(self.message_list, f"Failed to export tab_ad_igdef_df: {e}", status="f")

        # Save tab_ad_igdef_oid_desc
        file_path = os.path.join(file_path_base, "log_ad_ig_it.csv")
        try:
            self.tab_ad_igdef_oid_desc.to_csv(file_path, index=False)
            mtbp3cd.gui.util_show_message(self.message_list, f"ad_igdef_oid_desc saved: {file_path}", status="s")
        except Exception as e:
            mtbp3cd.gui.util_show_message(self.message_list, f"Failed to export ad_igdef_oid_desc: {e}", status="f")

        file_path = os.path.join(file_path_base, "log_ad_ig_it_flag.csv")
        try:
            self.tab_ad_flag_df.to_csv(file_path, index=False)
            mtbp3cd.gui.util_show_message(self.message_list, f"ad_igdef_oid_desc saved: {file_path}", status="s")
        except Exception as e:
            mtbp3cd.gui.util_show_message(self.message_list, f"Failed to export ad_igdef_oid_desc: {e}", status="f")

if __name__ == "__main__":
    pass