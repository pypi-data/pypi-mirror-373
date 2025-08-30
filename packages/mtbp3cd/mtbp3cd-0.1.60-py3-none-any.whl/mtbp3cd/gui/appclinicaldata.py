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


import sys, mtbp3cd 
from mtbp3cd.gui import gt01r_starting, gt03r_inputfolder, gt03o_define, gt03o_adsl
from PyQt6.QtCore import Qt

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

        self.sidebar_button_input = QPushButton("Select Input Folder")
        self.sidebar_button_input.clicked.connect(self.sidebar_button_input_f)
        self.sidebar_button_input.setCheckable(True)

        self.sidebar_button_ad_define = QPushButton("Define.xml")
        self.sidebar_button_ad_define.clicked.connect(self.sidebar_button_ad_define_f)
        self.sidebar_button_ad_define.setCheckable(True)

        self.sidebar_button_adsl = QPushButton("ADSL")
        self.sidebar_button_adsl.clicked.connect(self.sidebar_button_adsl_f)
        self.sidebar_button_adsl.setCheckable(True)

        self.all_buttons = [self.sidebar_button_starting, self.sidebar_button_input, self.sidebar_button_ad_define, self.sidebar_button_adsl]

        ###### Layout - SIDEBAR ######
        layout_sidebar = QVBoxLayout()
        layout_sidebar.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_sidebar.addWidget(QLabel("<b>Starts Here:</b>"))
        layout_sidebar.addWidget(self.sidebar_button_starting)
        layout_sidebar.addWidget(self.sidebar_button_input)
        layout_sidebar.addWidget(QLabel("<b>Data Exchange:</b>"))
        layout_sidebar.addWidget(self.sidebar_button_ad_define)
        layout_sidebar.addWidget(QLabel("<b>ADaM:</b>"))
        layout_sidebar.addWidget(self.sidebar_button_adsl)

        sidebar_widget = QWidget()
        sidebar_widget.setLayout(layout_sidebar)

        ###### TAB - ALL ######
        self.tab_starting = mtbp3cd.gui.gt01r_starting.TabStarting()
        self.tab_input = mtbp3cd.gui.gt03r_inputfolder.TabInput(self)
        self.tab_define = mtbp3cd.gui.gt03o_define.TabDefine(self)
        self.tab_adsl= mtbp3cd.gui.gt03o_adsl.TabADSL(self)

        self.tabs = QTabWidget()
        self.tabs.tabBar().setVisible(False)
        self.tabs.addTab(self.tab_starting, "View Output Folder")
        self.tabs.addTab(self.tab_input, "View Input Folder")
        self.tabs.addTab(self.tab_define, "View Define.xml")
        self.tabs.addTab(self.tab_adsl, "View adsl")

        ###### Layout - TAB - ALL ######
        layout_h = QHBoxLayout()
        layout_h.addWidget(sidebar_widget)
        layout_h.addWidget(self.tabs)
        self.setLayout(layout_h)

    def sidebar_button_starting_f(self):
        self.tabs.setCurrentWidget(self.tab_starting)
        mtbp3cd.gui.update_sidebar_buttons_f(self.all_buttons, self.sidebar_button_starting)

    def sidebar_button_input_f(self):
        self.tabs.setCurrentWidget(self.tab_input)
        mtbp3cd.gui.update_sidebar_buttons_f(self.all_buttons, self.sidebar_button_input)

    def sidebar_button_ad_define_f(self):
        self.tabs.setCurrentWidget(self.tab_define)
        mtbp3cd.gui.update_sidebar_buttons_f(self.all_buttons, self.sidebar_button_ad_define)

    def sidebar_button_adsl_f(self):
        self.tabs.setCurrentWidget(self.tab_adsl)
        mtbp3cd.gui.update_sidebar_buttons_f(self.all_buttons, self.sidebar_button_adsl)

class ClinicalDataApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clinical Data Tool")
        screen = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(screen.x(), screen.y(), int(screen.width()*0.75), int(screen.height()*0.75))
        self.main_widget = MainWedge()
        self.setCentralWidget(self.main_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ClinicalDataApp()
    window.show()
    sys.exit(app.exec())
