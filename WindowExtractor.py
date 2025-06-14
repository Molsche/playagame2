import win32gui
import pygetwindow as gw
from mss import mss
import numpy as np
import cv2

from constants import EXP_BAR_WIDTH, EXP_BAR_HEIGHT, EXP_BAR_PADDING, PLAYER_LEVEL_TOP, PLAYER_LEVEL_HIGHT, \
    PLAYER_LEVEL_WIDTH, PLAYER_LEVEL_LEFT, BARS_LEFT, HP_BAR_TOP, BAR_WIDTH, BAR_HEIGHT, MP_BAR_TOP, TEST_BAR_HEIGHT, \
    TEST_BAR_TOP, TEST_BARS_LEFT, TEST_BAR_WIDTH


def get_hwnd_of_title(title):
    return gw.getWindowsWithTitle(title)[0]._hWnd


def get_client_rect(hwnd):
    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    point = win32gui.ClientToScreen(hwnd, (0, 0))
    client_left = point[0]
    client_top = point[1]
    width = right - left
    height = bottom - top
    return {"left": client_left, "top": client_top, "width": width, "height": height}

def extract_sub_frame(img, bar_top, bar_left, bar_width, bar_hight):
    """Extract the HP bar region from a screenshot of the game window."""
    return img[bar_top:bar_top + bar_hight, bar_left:bar_left + bar_width]

def get_exp_bar_rect(image_width, image_height, bar_width=EXP_BAR_WIDTH, bar_height=EXP_BAR_HEIGHT, bar_padding=EXP_BAR_PADDING):
    """
    Calculate the rectangle coordinates for the EXP bar, centered at the bottom.
    If the window is narrower than 1600px, use the full width.
    """
    bar_width = min(bar_width, image_width - 12) # 6px Padding on each side = -12
    x = (image_width - bar_width) // 2
    y = image_height - bar_height - bar_padding
    return (x, y, bar_width, bar_height)

def isolate_white_pixels(img):
    if img.shape[2] == 4:
        img = img[:, :, :3]

    white_mask = np.all(img == [255, 255, 255], axis=-1)
    output = np.zeros_like(img)
    output[white_mask] = [255, 255, 255]
    return cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)

def isolate_red_pixels(img):
    if img.shape[2] == 4:
        img = img[:, :, :3]

    white_mask = np.all(img == [0, 0, 0], axis=-1)
    output = np.zeros_like(img)
    output[white_mask] = [255, 255, 255]
    # return cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)
    return output

def get_player_level_img(img):
    level_img = isolate_white_pixels(
            extract_sub_frame(img, PLAYER_LEVEL_TOP, PLAYER_LEVEL_LEFT, PLAYER_LEVEL_WIDTH, PLAYER_LEVEL_HIGHT)
    )
    return level_img

def get_player_hp_bar_img(img):
    hp_bar_img = extract_sub_frame(img, HP_BAR_TOP, BARS_LEFT, BAR_WIDTH, BAR_HEIGHT)
    # hp_bar_img = extract_sub_frame(img, TEST_BAR_TOP, TEST_BARS_LEFT, TEST_BAR_WIDTH, TEST_BAR_HEIGHT)
    cv2.destroyAllWindows()
    return hp_bar_img

def get_player_mp_bar_img(img):
    hp_bar_img = extract_sub_frame(img, MP_BAR_TOP, BARS_LEFT, BAR_WIDTH, BAR_HEIGHT)
    return hp_bar_img

def get_player_exp_bar_img(img, bar_width=EXP_BAR_WIDTH, bar_height=EXP_BAR_HEIGHT, bar_padding=EXP_BAR_PADDING):
    h, w, _ = img.shape
    x, y, bw, bh = get_exp_bar_rect(w, h, bar_width, bar_height, bar_padding)
    return img[y:y + bh, x:x + bw]


def get_region_of_window(windowtitle):
    hwnd = get_hwnd_of_title(windowtitle)
    return get_client_rect(hwnd)

def get_player_info_images(region, debug=False):
    img = get_image_in_BGR(region, debug)
    player_level_img = get_player_level_img(img)
    player_hp_img = get_player_hp_bar_img(img)
    player_mp_img = get_player_mp_bar_img(img)
    player_exp_img = get_player_exp_bar_img(img)
    return [player_hp_img, player_mp_img, player_level_img, player_exp_img]

def get_img_in_RGB(region):
    with mss() as sct:
        img = np.array(sct.grab(region))
        if img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
        return img

def get_image_in_BGR(region, debug=False):
    with mss() as sct:
        img = np.array(sct.grab(region))
        if img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
        if debug:
            cv2.imshow("full img", img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        return img


def threshold_r_channel(img_bgr, threshold=150):
    """Set all pixels with R >= threshold to 255, and below to 0."""
    img = img_bgr.copy()
    # Split BGR channels
    b, g, r = cv2.split(img)

    # Apply threshold to R channel
    r = np.where(r >= threshold, 255, 0).astype(np.uint8)

    # Recombine channels (keep B and G as is, or set them to 0 if you want only red info)
    b[:] = 0
    g[:] = 0

    result = cv2.merge([b, g, r])
    return result

def threshold_b_channel(img_bgr, threshold=150):
    """Set all pixels with B >= threshold to 255, and below to 0."""
    img = img_bgr.copy()
    # Split BGR channels
    b, g, r = cv2.split(img)
    # Apply threshold to R channel
    b = np.where(r >= threshold, 255, 0).astype(np.uint8)
    # Recombine channels (keep B and G as is, or set them to 0 if you want only red info)
    r[:] = 0
    g[:] = 0

    result = cv2.merge([b, g, r])
    return result

def threshold_g_channel(img_bgr, threshold=150):
    """Set all pixels with G >= threshold to 255, and below to 0."""
    img = img_bgr.copy()
    # Split BGR channels
    b, g, r = cv2.split(img)
    # Apply threshold to R channel
    g = np.where(r >= threshold, 255, 0).astype(np.uint8)
    # Recombine channels (keep B and G as is, or set them to 0 if you want only red info)
    r[:] = 0
    b[:] = 0

    result = cv2.merge([b, g, r])
    return result

if __name__ == "__main__":
    flo_hwnd = get_hwnd_of_title("Florensia")
    region = get_client_rect(flo_hwnd)


    img = get_image_in_BGR(region)

    hp_rect = (BARS_LEFT, HP_BAR_TOP, BAR_WIDTH, BAR_HEIGHT)
    mp_rect = (BARS_LEFT, MP_BAR_TOP, BAR_WIDTH, BAR_HEIGHT)
    level_rect = (PLAYER_LEVEL_LEFT, PLAYER_LEVEL_TOP, PLAYER_LEVEL_WIDTH, PLAYER_LEVEL_HIGHT)
    h, w, _ = img.shape
    exp_rect = get_exp_bar_rect(w, h)


    for (x, y, w_, h_) in [hp_rect, mp_rect, exp_rect, level_rect]:
        cv2.rectangle(img, (x, y), (x + w_, y + h_), (0, 255, 0), 2)  # Green box

    # img_hp = extract_bar(img, HP_BAR_TOP, BARS_LEFT, BAR_WIDTH, BAR_HEIGHT)
    cv2.imshow("Cropped Game Only", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()