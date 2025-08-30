from .utils import *

from PyQt5.QtWidgets import QApplication
import sys

from .qt_adjust import fix_qt_plugin_paths, assert_not_using_cv2_plugins
# from .safe_cv import im



from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QFileDialog, QMessageBox, QLineEdit, QHBoxLayout, QGroupBox, QCheckBox
from PyQt5.QtGui import QPixmap, QPainter, QPen, QImage, QMouseEvent, QColor
from PyQt5.QtCore import Qt, QPoint, QRect, QFileInfo
import cv2
from fabio.edfimage import EdfImage
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import numpy
import matplotlib.pyplot as plt
import string
from PIL import Image
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.pdfgen import canvas
from reportlab.lib import colors

import copy
import time as timelib
from datetime import datetime
from datetime import timedelta
import numpy as np
import sys
import re
import argparse
import matplotlib

import matplotlib.pyplot as plt

matplotlib.use('Agg')





def main_gui():
    
    
    fix_qt_plugin_paths(prefer_platform=None)
    
    app = QApplication(sys.argv)
    cropper = ImageCropper()
    
    
    
    try:
        assert_not_using_cv2_plugins()
    except RuntimeError as e:
        # Mostre uma mensagem amigável e encerre
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.critical(None, "Qt plugin error", str(e))
        sys.exit(1)
    
    
    
    sys.exit(app.exec_())


