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


"""
File Inventory Tool GUI

This module provides the graphical user interface for the File Inventory Tool, built using PyQt6.
It organizes the workflow into a sidebar and tabbed interface, allowing users to navigate between
different sections of the application.

    MainWedge (QWidget):
        - Main widget containing the sidebar and tabbed interface.
        - Sidebar provides navigation buttons for:
            * "Select Output Folder"
            * "Select Input Folder"
            * "Checksum"
            * "Compare Record"
        - Each button switches the main view to the corresponding tab.
        - Tabs are:
            * Output folder selection/viewing
            * Input folder selection/viewing
            * File checksums viewing
            * Record comparison

    FileInventoryApp (QMainWindow):
        - Main application window.
        - Sets up window properties and embeds the MainWedge widget.

    - mtbp3cd (local package)

    Run this module directly to launch the File Inventory Tool GUI.

License:
    GNU General Public License v3.0 or later

Author:
    Y Hsu <yh202109@gmail.com>
"""
import sys
import mtbp3cd
from PyQt6.QtCore import Qt
from mtbp3cd.gui import gt01r_starting, gt01r_inputfolder,  gt01o_checksum, gt01o_record

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, 
    QVBoxLayout, QHBoxLayout, 
    QTabWidget, QPushButton, QLabel,
)

class MainWedge(QWidget):
    def __init__(self):
        super().__init__()

        ###### SIDEBAR ######
        self.sidebar_button_starting = QPushButton("Select Output Folder")
        self.sidebar_button_starting.setStyleSheet(mtbp3cd.gui.style_btn_clicked)
        self.sidebar_button_starting.clicked.connect(self.sidebar_button_starting_f)
        self.sidebar_button_starting.setCheckable(True)

        self.sidebar_button_folder = QPushButton("Select Input Folder")
        self.sidebar_button_folder.clicked.connect(self.sidebar_button_folder_f)
        self.sidebar_button_folder.setCheckable(True)

        self.sidebar_button_checksum = QPushButton("Checksum")
        self.sidebar_button_checksum.clicked.connect(self.sidebar_button_checksum_f)
        self.sidebar_button_checksum.setCheckable(True)

        self.sidebar_button_record = QPushButton("Compare Record")
        self.sidebar_button_record.clicked.connect(self.sidebar_button_record_f)
        self.sidebar_button_record.setCheckable(True)

        self.all_buttons = [self.sidebar_button_starting, self.sidebar_button_folder, self.sidebar_button_checksum, self.sidebar_button_record]

        ###### Layout - SIDEBAR ######
        layout_sidebar = QVBoxLayout()
        layout_sidebar.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_sidebar.addWidget(QLabel("<b>Starts Here:</b>"))
        layout_sidebar.addWidget(self.sidebar_button_starting)
        layout_sidebar.addWidget(self.sidebar_button_folder)
        layout_sidebar.addWidget(QLabel("<b>Task:</b>"))
        layout_sidebar.addWidget(self.sidebar_button_checksum)
        layout_sidebar.addWidget(self.sidebar_button_record)

        sidebar_widget = QWidget()
        sidebar_widget.setLayout(layout_sidebar)

        ###### TAB - ALL ######
        self.tab_starting = mtbp3cd.gui.gt01r_starting.TabStarting()
        self.tab_folder = mtbp3cd.gui.gt01r_inputfolder.TabFolder(self)
        self.tab_checksum = mtbp3cd.gui.gt01o_checksum.TabChecksum(self)
        self.tab_record = mtbp3cd.gui.gt01o_record.TabRecord(self)

        self.tabs = QTabWidget()
        self.tabs.tabBar().setVisible(False)
        self.tabs.addTab(self.tab_starting, "View Output Folder")
        self.tabs.addTab(self.tab_folder, "View Input Folder")
        self.tabs.addTab(self.tab_checksum, "View Checksums")
        self.tabs.addTab(self.tab_record, "View Record")

        ###### Layout - TAB - ALL ######
        layout_h = QHBoxLayout()
        layout_h.addWidget(sidebar_widget)
        layout_h.addWidget(self.tabs)
        self.setLayout(layout_h)

    def sidebar_button_starting_f(self):
        self.tabs.setCurrentWidget(self.tab_starting)
        mtbp3cd.gui.update_sidebar_buttons_f(self.all_buttons, self.sidebar_button_starting)

    def sidebar_button_folder_f(self):
        self.tabs.setCurrentWidget(self.tab_folder)
        mtbp3cd.gui.update_sidebar_buttons_f(self.all_buttons, self.sidebar_button_folder)

    def sidebar_button_checksum_f(self):
        self.tabs.setCurrentWidget(self.tab_checksum)
        mtbp3cd.gui.update_sidebar_buttons_f(self.all_buttons, self.sidebar_button_checksum)

    def sidebar_button_record_f(self):
        self.tabs.setCurrentWidget(self.tab_record)
        mtbp3cd.gui.update_sidebar_buttons_f(self.all_buttons, self.sidebar_button_record)

class FileInventoryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Inventory Tool")
        self.setGeometry(100, 100, 800, 600)
        self.main_widget = MainWedge()
        self.setCentralWidget(self.main_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileInventoryApp()
    window.show()
    sys.exit(app.exec())
