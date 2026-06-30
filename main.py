from gui_app import SensorGUI
from config import CURRENT_FOLDER, TRAINING_FOLDER

def main():
    app = SensorGUI(current_folder=CURRENT_FOLDER, training_folder=TRAINING_FOLDER)
    app.run()
if __name__ == "__main__": main()
