import cv2 as cv

MAX_CAMERA_INDEX = 10 # Arbitrary number, average use case user will have max 2 cameras
    

def get_camera_names() :
    """
    Scans device for available cameras
    """
    try : 
        from pygrabber.dshow_graph import FilterGraph # So Windows DirectShow names can be read

        graph = FilterGraph()

        return graph.get_input_devices()
    
    except Exception : 
        return []
    

def camera_can_capture(index) : 
    """
    Checks if camera index can open and return a frame
    """
    cap = cv.VideoCapture(index, cv.CAP_DSHOW)

    if not cap.isOpened() : 
        cap.release() # Release just in case
        return False
    
    success, frame = cap.read()
    cap.release()
    
    return success and frame is not None # Camera produced a real frame


def scan_available_cameras()  :
    """
    Scans available cameras
    """

    camera_names = get_camera_names()
    available_cameras = []

    for index in range(MAX_CAMERA_INDEX) : 
        #if camera_can_capture(index) : 
        # Check if index has matching DirectShow name
        if index < len(camera_names) : 
            camera_name = camera_names[index]

        else : # No real name exists
            camera_name = f"Camera {index}"

        # Create readable label
        camera_label = f"[{index + 1}] {camera_name}"
        available_cameras.append(
            {
                "index": index,
                "name": camera_name,
                "label": camera_label
            }
        )

        return available_cameras