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


def main_terminal():

    function = choose_funtion();

    if function == 1:
        video_file = get_video_file();
        print("Wait, This operation may take some time.")
        infos = get_info_video();
        set_file_1 = conc_scat_video(3, file_video = video_file, px_mm = infos[5] , step = infos[0], time_limit = infos[6], retangulo = [infos[1], infos[2], infos[3],infos[4]]  );
        set_file_1.read_video();
    elif function == 2:
        directory, root_file, _ = get_dir_paths(get_file_root = True);
        set_file_1 = conc_scat_video(4,path = directory, root_name = root_file);
        set_file_1.read_setfiles_edf(option = 1);
    elif function == 3:
        directory, root_file, file_path = get_dir_paths(get_file_root = True, get_file_path = True);
        set_file_1 = conc_scat_video(5,path = directory, root_name = root_file, input_file = file_path);
        set_file_1.read_setfiles_edf(option = 0);
    elif function == 4:
        print("\nNow TYPE information about SAMPLES.")
        directory, root_file, file_path = get_dir_paths(get_file_path = True);
        set_file_1 = conc_scat_video(5,path = directory, input_file = file_path);
        set_file_1.read_setfiles_edf(option = 2);

        print("\nNow TYPE information about BACKGROUND.")
        directory, _, file_path = get_dir_paths(get_file_path = True);
        set_file_2 = conc_scat_video(5,path = directory, input_file = file_path);
        set_file_2.read_setfiles_edf(option = 2);

        concatene_files_scat_back(set_file_1, set_file_2);
