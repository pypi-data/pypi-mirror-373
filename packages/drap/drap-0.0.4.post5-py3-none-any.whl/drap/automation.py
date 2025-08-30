from .utils import *


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



def main_batch():
    
    
    list_files = 'name_videos.dat';

    set_file_1 = conc_scat_video(1, file_in = list_files);

    set_file_1.read_video();
    # print("Fimm ---")
    # exit(0)
    set_file_1.read_setfiles_edf(option = 1);
    set_file_1.read_setfiles_edf(option = 0);
    set_file_1.read_setfiles_edf();
    # print("Fimm ---")
    # exit(0)

    set_file_2 = conc_scat_video(2, file_in = list_files);
    set_file_2.read_video();
    set_file_2.read_setfiles_edf(option = 0);
    set_file_2.read_setfiles_edf(option = 1);
    set_file_2.read_setfiles_edf();

    concatene_files_scat_back(set_file_1, set_file_2);

