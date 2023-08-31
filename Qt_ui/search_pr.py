import sys
import os
from PyQt5.QtMultimedia import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtMultimediaWidgets import *
from Qt_ui._ui.ui_join_form import Ui_joinForm
from ultralytics import YOLO
from glob import glob
from time import sleep
from PIL.ImageFont import *
from PIL.Image import *
from PIL.ImageDraw import *
import cv2
import easyocr
import threading
import matplotlib.pyplot as plt
import warnings
import random
import numpy as np
import psycopg2
from Qt_ui.interaction_db import InteractionToDB
import datetime
import time
from threading import Thread
from PIL import ImageFont, ImageDraw, Image

from Qt_ui._ui.search_ui import Ui_MainWindow

class Search(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()





if __name__ == '__main__':
    app = QApplication(sys.argv)
    run = Search()
    run.show()
    app.exec_()

