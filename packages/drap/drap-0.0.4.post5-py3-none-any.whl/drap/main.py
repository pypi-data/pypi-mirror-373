

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
import os
import copy
import time as timelib
from datetime import datetime
from datetime import timedelta
import numpy as np
import sys
import re
import argparse
import cv2
import matplotlib

import matplotlib.pyplot as plt

matplotlib.use('Agg')


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--option", type=int, help="Execution mode: 1=GUI, 2=Terminal, 3=Batch")
    args = parser.parse_args()

    if args.option == 1:
        from .gui import main_gui
        main_gui()
    elif args.option == 2:
        from .terminal_interface import main_terminal
        main_terminal()
    elif args.option == 3:
        from .automation import main_batch
        main_batch()
    else:
        print("Use -o [1|2|3] to select a mode.")





















