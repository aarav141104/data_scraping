import pyautogui
import time


# Function to get mouse position
def get_mouse_position():
    while True:
        # Capture the current mouse position
        x, y = pyautogui.position()
        print(f"Mouse position: (x={x}, y={y})")
        time.sleep(1)  # Print the position every second


# Give yourself some time to move the mouse to the desired position
print("Move the mouse to the desired position within the next 5 seconds...")
time.sleep(5)

# Get the mouse position
get_mouse_position()
