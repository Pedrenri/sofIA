import os
import subprocess
import time
import pyautogui
from pyautogui import ImageNotFoundException

def run_os_command(command: str) -> str:
    """
    Execute an OS system command and return its output.
    """
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip() if result.stdout.strip() else result.stderr.strip()
    except Exception as e:
        return str(e)

def print_message(message: str) -> str:
    """
    Print a message in the terminal and return an acknowledgement.
    """
    print(f"Jarvis Print: {message}")
    return f"Printed: {message}"

def print_stl(stl_file: str, pc_username: str = None) -> str:
    """
    Open an STL file with the default associated application using subprocess.run,
    then click through a series of images to initiate printing.
    
    The STL file path can use environment variables (e.g., %USERPROFILE%) or ~ for home.
    Additionally, if the file path contains "YourUsername", it is replaced with the
    provided pc_username (or the PC_USERNAME environment variable).
    
    Returns a success or error message.
    """
    try:
        # If a username is provided, use it; otherwise, get it from the environment.
        if pc_username is None:
            pc_username = os.getenv("PC_USERNAME", "YourUsername")
        
        # Replace "YourUsername" placeholder with the actual PC username.
        stl_file = stl_file.replace("YourUsername", pc_username)
        
        # Expand environment variables and user home directory in the provided path.
        stl_file_expanded = os.path.expandvars(stl_file)
        stl_file_expanded = os.path.expanduser(stl_file_expanded)
        print(f"Expanded STL file path: {stl_file_expanded}")
        
        # Check if the file exists
        if not os.path.exists(stl_file_expanded):
            return f"Error: File not found at {stl_file_expanded}"
        
        # Open the STL file using subprocess.run.
        command = f'start "" "{stl_file_expanded}"'
        print(f"Executing command: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.stderr:
            print("Error opening STL file:", result.stderr)
            return f"Error opening STL file: {result.stderr}"
        
        # Wait for the application to open (adjust delay as needed)
        time.sleep(10)
        
        # Define image paths for the printing workflow
        images = [
            './bambu_print/slice.jpg',
            './bambu_print/print.jpg',
            './bambu_print/send.jpg'
        ]
        confidence_threshold = 0.99
        
        for image in images:
            print(f'Waiting for {image}...')
            while True:
                try:
                    location = pyautogui.locateOnScreen(image, confidence=confidence_threshold)
                    if location:
                        x, y = pyautogui.center(location)
                        print(f'Found {image}, clicking at ({x}, {y})')
                        pyautogui.click(x, y)
                        time.sleep(3)  # Pause briefly after each click
                        break
                except ImageNotFoundException:
                    time.sleep(0.5)
        return "STL file printed successfully."
    except Exception as e:
        return f"Error printing STL: {str(e)}"
