import cv2 as cv
from camera_settings import apply_camera_profile

def open_camera(index): # Fixed settings to avoid changing variables
    cap = cv.VideoCapture(index) # Open camera
    return cap


def set_normal_exposure(cap):
    print("Normal settings applied")
    apply_camera_profile(cap, "normal")

def set_low_exposure(cap):
    print("Low exposure settings applied")
    apply_camera_profile(cap, "low")

def grab_frame(cap, settleFrames = 10):   # Settle time for camera
    for i in range(settleFrames):
        cap.read()

    success,frame = cap.read()
    if not success:
        return None
    
    return frame