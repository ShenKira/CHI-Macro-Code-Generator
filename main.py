# -*- coding: utf-8 -*-
"""
Created on Tue Dec 30 12:08:59 2025

@author: shenz
"""

import sys
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow
from PySide6.QtGui import QFont

app = QApplication(sys.argv)
font = QFont()
font.setPointSizeF(font.pointSizeF() * 1.5)
app.setFont(font)
window = MainWindow()
window.show()
sys.exit(app.exec())
