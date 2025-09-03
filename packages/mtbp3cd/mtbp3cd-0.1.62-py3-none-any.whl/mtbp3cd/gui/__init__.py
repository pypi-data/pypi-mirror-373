import sys
from PyQt6.QtWidgets import QApplication
from .appfileinventory import *
from .appclinicaldata import *

style_btn_clicked = "QPushButton { background-color: #0078d7; color: white; border: none; padding: 3px 16px; border-radius: 4px; }"

def update_sidebar_buttons_f(all_buttons=None, clicked_button=None):
    if not isinstance(all_buttons, list) or not all_buttons:
        return
    if clicked_button not in all_buttons:
        return
        
    for btn in all_buttons:
        if btn is clicked_button:
            btn.setStyleSheet(style_btn_clicked)
            btn.setChecked(True)
        else:
            btn.setStyleSheet("")
            btn.setChecked(False)

def util_show_message(message_list, message, status="info"):
    color_map = {
        "warning": Qt.GlobalColor.darkYellow,
        "w": Qt.GlobalColor.darkYellow,
        "success": Qt.GlobalColor.darkGreen,
        "s": Qt.GlobalColor.darkGreen,
        "fail": Qt.GlobalColor.darkRed,
        "f": Qt.GlobalColor.darkRed,
        "info": Qt.GlobalColor.darkBlue,
        "i": Qt.GlobalColor.darkBlue
    }
    color = color_map.get(status, Qt.GlobalColor.black)
    message_list.addItem(message)
    message_list.item(message_list.count() - 1).setForeground(color)
    message_list.scrollToBottom()

def runapp(type="FileInventory"):
    if isinstance(type, str):
        if type == "FileInventory":
            app = QApplication(sys.argv)
            windows = FileInventoryApp()
            windows.show() 
            sys.exit(app.exec())

        if type == "ClinicalData":
            app = QApplication(sys.argv)
            windows = ClinicalDataApp()
            windows.show() 
            sys.exit(app.exec())
