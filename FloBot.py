import json
import time
import torch

from ExpRecognizer import ExpRecognizer
from HpRecognizer import HpRecognizer
from MpRecognizer import MpRecognizer
from LevelRecognizer import LevelRecognizer
from WindowExtractor import get_region_of_window, get_player_info_images
from YoloEye import YoloEye


class FloBot:

    def __init__(self):
        self.hp_recognizer = HpRecognizer()
        self.mp_recognizer = MpRecognizer()
        self.level_recognizer = LevelRecognizer()
        self.exp_recognizer = ExpRecognizer()
        self.region = get_region_of_window("Florensia")
        self.yolo_eye = YoloEye(self.region, 'yolov5x6')

        self.level_timer = time.time()

        self.hp, self.mp, self.level, self.exp = self.detect_all_player_stats()
        with open('data/land_monster_data.json', 'r') as f:
            self.monsters = json.load(f)


        # print("player level: ", self.level)
        # print("player exp: ", self.exp)
        # print("player hp: ", self.hp[0], "/", self.hp[1])
        # print("player mp: ", self.mp[0], "/", self.mp[1])
        self.ACTIVE = True

    def detect_player_hp_mp(self):
        player_info_img_array = get_player_info_images(self.region, False)
        hp = self.hp_recognizer.recognize_player_hp(player_info_img_array[0])
        mp = self.mp_recognizer.recognize_player_mp(player_info_img_array[1])
        return [hp, mp]

    def detect_all_player_stats(self):
        player_info_img_array = get_player_info_images(self.region, False)
        level = self.level_recognizer.recognize_player_level(player_info_img_array[2])
        hp = self.hp_recognizer.recognize_player_hp(player_info_img_array[0])
        mp = self.mp_recognizer.recognize_player_mp(player_info_img_array[1])
        exp = self.exp_recognizer.recognize_player_exp(player_info_img_array[3])
        return [hp, mp, level, exp]

    def test_function(self):
        loop_time = time.time()
        i = 0
        while i <= 1:
            self.hp, self.mp, self.level, self.exp = self.detect_all_player_stats()
            print('FPS: {}'.format(1 / (time.time() - loop_time)))
            i += 1
            loop_time = time.time()

            print("Level:", self.level,
                  "||   exp:", self.exp,
                  "||   hp:", self.hp[0], "/", self.hp[1],
                  "||   mp:", self.mp[0], "/", self.mp[1])
            detections = self.yolo_eye.run_yolo_detection()
            print("YOLO Detections:", detections)




if __name__ == "__main__":
    print("run")
    bot = FloBot()
    bot.test_function()