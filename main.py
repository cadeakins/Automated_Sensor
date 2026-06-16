import cv2 as cv
import matplotlib.pyplot as plt
from datetime import datetime
import time


from organism_menu import choose_organism
from experiment_controller import ExperimentController
from gui_app import SensorGUI

def main():
    app = SensorGUI()
    app.run()
if __name__ == "__main__": main()
