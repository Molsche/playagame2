from miscellaneous import get_florensia_window_region
import cv2
import time
import mss
import numpy as np
import shutil

monitor = get_florensia_window_region()
sct = mss.mss()


def main_loop():
    print("Starting screen capture...")
    i = 0
    while True:
        i += 1
        time.sleep(1)
        print("taking_screenshot " + str(i))
        screenshot = sct.grab(monitor)
        time_string = f"_{int(time.time())}"
        filename = "simple" + time_string
        if i % 7 == 0:
            png = f"data/images/val/" + filename + ".png"
            txt = f"data/labels/val/" + filename + ".txt"
            img = np.array(screenshot)
            cv2.imwrite(png, img)
            shutil.copy("data/blueprints/simple_labels_with_only_sit.txt", txt)
        else:
            png = f"data/images/train/" + filename + ".png"
            txt = f"data/labels/train/" + filename + ".txt"
            img = np.array(screenshot)
            cv2.imwrite(png, img)
            shutil.copy("data/blueprints/simple_labels_with_only_sit.txt", txt)

if __name__ == "__main__":
    main_loop()