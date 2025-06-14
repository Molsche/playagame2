import os
import cv2
import numpy as np

class MpRecognizer:
    def __init__(self, template_path="data/digits_templates/digits_mp", match_threshold=0.8):
        self.template_path = template_path
        self.match_threshold = match_threshold
        self.templates = self.load_templates()

    def load_templates(self):
        templates = {}
        for filename in os.listdir(self.template_path):
            if filename.endswith(".png"):
                label = filename[:-5]  # "1l.png" -> "1"
                char = label[0]
                img = cv2.imread(os.path.join(self.template_path, filename))
                templates[filename] = (char, img)
        return templates

    def suppress_duplicates(self, matches, min_dist=5):
        filtered = []
        last_x = -min_dist
        for x, digit in sorted(matches):
            if x - last_x >= min_dist:
                filtered.append((x, digit))
                last_x = x
        return filtered

    def match_digit_templates(self, digit_img):

        matches = []
        for name, (char, tmpl) in self.templates.items():
            res = cv2.matchTemplate(digit_img, tmpl, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= self.match_threshold)
            for pt in zip(*loc[::-1]):
                matches.append((pt[0], char))

        matches = self.suppress_duplicates(matches)
        text = ''.join([digit for _, digit in matches])
        if '%' in text:
            parts = text.split('%')
            try:
                return [int(parts[0]), int(parts[1])]
            except:
                return None
        return None

    def recognize_player_mp(self, digit_img):
        return self.match_digit_templates(digit_img)
