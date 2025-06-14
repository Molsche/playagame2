import time

import numpy as np
import cv2

from constants import MP_BAR_FILL_COLOR_BGR, EXP_BAR_FILL_COLOR_BGR, HP_BAR_FILL_COLOR_BGR, HP_BAR_FILL_COLOR_RGB


def calculate_fill_percent(img_bgr, fill_color_bgr, tolerance=10, debug=False):
    """Calculate fill percent of a horizontal bar by matching a BGR fill color with some tolerance."""
    if debug:
        print(img_bgr.shape)
        cv2.imshow("frame",img_bgr)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    # time.sleep(5)
    lower = np.array([max(0, c - tolerance) for c in fill_color_bgr], dtype=np.uint8)
    upper = np.array([min(255, c + tolerance) for c in fill_color_bgr], dtype=np.uint8)

    mask = cv2.inRange(img_bgr, lower, upper)

    # Use middle row for stability (can average a few rows for better robustness)
    middle_row = mask[mask.shape[0] // 2]
    filled_pixels = cv2.countNonZero(middle_row)
    total_pixels = mask.shape[1]

    return round(filled_pixels / total_pixels * 100, 2)

def calculate_fill_percent_by_scan(img_bgr, fill_color_bgr, tolerance=10):
    lower = np.array([max(0, c - tolerance) for c in fill_color_bgr], dtype=np.uint8)
    upper = np.array([min(255, c + tolerance) for c in fill_color_bgr], dtype=np.uint8)

    mask = cv2.inRange(img_bgr, lower, upper)
    middle_row = mask[mask.shape[0] // 2]

    # Scan from right to left
    for x in reversed(range(len(middle_row))):
        if middle_row[x] > 0:
            return round(x / len(middle_row) * 100, 2)

    return 0.0  # fallback

def get_hp_percent(img_bgr, debug=False):
    return calculate_fill_percent_by_scan(img_bgr, HP_BAR_FILL_COLOR_BGR, tolerance=20)

def get_exp_percent(img_bgr, debug=False):
    return calculate_fill_percent(img_bgr, EXP_BAR_FILL_COLOR_BGR, tolerance=10)