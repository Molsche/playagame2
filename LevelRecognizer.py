import cv2
import numpy as np

class LevelRecognizer:

    def __init__(self, template_path="data/digits_templates/level", match_threshold=0.95):
        self.template_path = template_path
        self.match_threshold = match_threshold
        self.templates = self.load_templates()

    def load_templates(self):
        templates = {}
        for i in range(10):
            path = f"{self.template_path}/{i}.png"
            tmpl = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            templates[str(i)] = tmpl
        return templates

    def recognize_player_level(self, level_img):
        matches = []

        for digit, tmpl in self.templates.items():
            res = cv2.matchTemplate(level_img, tmpl, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= self.match_threshold)
            for pt in zip(*loc[::-1]):
                matches.append((pt[0], digit))  # x-position, digit
        # Sort by X (left to right)
        matches.sort()
        level = ''.join([digit for _, digit in matches])
        return int(level) if level else None


def recognize_player_level(img):
    templates = load_templates()
    level = match_digit_templates(img, templates)
    return level

def match_digit_templates(level_img, templates):
    matches = []

    for digit, tmpl in templates.items():
        res = cv2.matchTemplate(level_img, tmpl, cv2.TM_CCOEFF_NORMED)
        threshold = 0.95  # You might need to tune this
        loc = np.where(res >= threshold)
        for pt in zip(*loc[::-1]):
            matches.append((pt[0], digit))  # x-position, digit

    # Sort by X (left to right)
    matches.sort()
    level = ''.join([digit for _, digit in matches])
    return int(level) if level else None

def load_templates(template_dir="data/digits_templates/level"):
    templates = {}
    for i in range(10):
        path = f"{template_dir}/{i}.png"
        tmpl = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        templates[str(i)] = tmpl
    return templates
