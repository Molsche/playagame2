import os
import time
import io
import csv

import cv2
import numpy as np
from selenium import webdriver
from selenium.webdriver import FirefoxProfile
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from PIL import Image, ImageGrab
import requests
import json
import pyautogui

def get_all_monsters():
    url = "https://flandria.wiki/api/graphql"

    query = """
        query AllMonsters($is_sea: BooleanFilter = {eq: false}) {
            all_monsters(limit: 1000, order_by: {level: ASC}, filter: {is_sea: $is_sea}) {
                items {
                    code
                    name
                    model_name
                    level
                    health_points
                    physical_defense
                    magical_defense
                    minimum_physical_damage
                    maximum_physical_damage
                    minimum_magical_damage
                    maximum_magical_damage
                    is_ranged
                    attack_range
                    attack_vision_range
                    nearby_attack_vision_range
                    experience
                    attack_vision_range
                    running_speed
                    icon
                }
            }
        }"""
    response = requests.post(url, json={"query": query})
    # response.raise_for_status()
    with open('data/response.json', 'w') as f:
        json.dump(response.json(), f)

def transform_data_to_monsters_json():
    with open('data/response.json', 'r') as f:
        data = json.load(f)
        items = data["data"]["all_monsters"]["items"]
        print(len(items))
        monsters = {}
        for monster in items:
            monsters[monster["name"]] = monster

        with open('data/land_monster_data.json', 'w') as w:
            json.dump(monsters, w)

def scrape_monsters():
    # Konfiguration
    BASE_URL = "https://flandria.wiki/database/monster"
    OUTPUT_DIR = "scraped_monsters"
    IMG_DIR = os.path.join(OUTPUT_DIR, "images")
    CSV_PATH = os.path.join(OUTPUT_DIR, "monsters.csv")
    os.makedirs(IMG_DIR, exist_ok=True)

    # Browser konfigurieren
    options = Options()
    # options.add_argument("--headless")  # Ohne UI
    driver = webdriver.Firefox(options=options)

    # Monsterliste laden
    driver.get(BASE_URL)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    cards = soup.select(".monster-card")  # ggf. anpassen

    # CSV vorbereiten
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as csvf:
        writer = csv.writer(csvf)
        writer.writerow(["name", "detail_url", "image_file"])

        for idx, card in enumerate(cards):
            name = card.select_one(".monster-name").text.strip()
            detail_link = card.select_one("a")["href"]
            detail_url = "https://flandria.wiki" + detail_link

            # Monster-Detailseite öffnen
            driver.get(detail_url)
            time.sleep(2)
            soup2 = BeautifulSoup(driver.page_source, "html.parser")
            img_elem = soup2.select_one(".model-viewer img")  # ggf. anpassen
            img_url = img_elem["src"] if img_elem else None

            # Screenshot des Bildbereichs
            if img_url:
                element = driver.find_element("css selector", ".model-viewer img")  # ggf. anpassen
                png = driver.get_screenshot_as_png()
                im = Image.open(io.BytesIO(png))
                loc = element.location; sz = element.size
                crop = im.crop((loc["x"], loc["y"], loc["x"] + sz["width"], loc["y"] + sz["height"]))
                fname = f"{idx:04d}_{name}.png".replace(" ", "_")
                crop.save(os.path.join(IMG_DIR, fname))
            else:
                fname = ""

            writer.writerow([name, detail_url, fname])
            print(f"Saved: {name} → {fname}")

    driver.quit()

def record_monster_screenshots(monster_name, val_dir, train_dir, duration=70, interval=0.5, val_every_n=5,
                               mouse_drag_distance=100, region=(100, 150, 655, 385)):
    # region Links, oben, rechts, unten
    """
    Nimmt für 'duration' Sekunden alle 'interval' Sekunden einen Screenshot auf.
    Jeder n-te Screenshot wird in val_dir gespeichert, die anderen in train_dir.
    Nach der Hälfte der Zeit wird die Maus gezogen, um die Perspektive zu ändern.
    """
    start_time = time.time()
    counter = 0
    switch_time = start_time + duration / 2
    did_drag = False

    left, top, right, bottom = region
    center_x = left + (right - left) // 2
    center_y = top + (bottom - top) // 2

    while time.time() - start_time < duration:
        now = time.time()
        filename = f"frame_{counter:04d}.png"
        path = os.path.join(val_dir if counter % val_every_n == 0 else train_dir, filename)

        screenshot = ImageGrab.grab(bbox=region) # Links, oben, rechts, unten
        cropped = crop_to_content(screenshot)
        cropped.save(path)

        print(f"[{monster_name}] Saved screenshot → {path}")
        counter += 1
        time.sleep(interval)

        # Perspektive ändern nach halber Zeit
        if not did_drag and now >= switch_time:
            print(f"[{monster_name}] Changing camera perspective...")
            pyautogui.moveTo(center_x, center_y, duration=0.1)
            pyautogui.mouseDown()
            pyautogui.moveRel(0, mouse_drag_distance, duration=0.1)
            pyautogui.mouseUp()
            did_drag = True

def get_screenshots_of_monsters():
    tuples = get_monster_code_name_tupels()
    base_url = "https://flandria.wiki/database/monster/"
    options = Options()
    profile = FirefoxProfile()
    profile.set_preference("layout.css.devPixelsPerPx", "0.6")
    options.profile = profile
    driver = webdriver.Firefox(options=options)
    driver.fullscreen_window()
    for monster in tuples:
        detail_url = base_url + monster[1]
        output_val_dir = f'data/monster_images/{monster[1]}/val'
        output_train_dir = f'data/monster_images/{monster[1]}/train'
        os.makedirs(output_val_dir, exist_ok=True)
        os.makedirs(output_train_dir, exist_ok=True)
        driver.get(detail_url)
        time.sleep(5)
        print(f"[{monster[0]}] Recording screenshots...")
        record_monster_screenshots(monster[1], output_val_dir, output_train_dir)

    driver.quit()

def get_monster_code_name_tupels():
    with open('data/land_monster_data.json', 'r') as f:
        data = json.load(f)
        tuples = []
        icon = []
        for name, monster_data in data.items():
            i = monster_data.get("icon", "")
            if i not in icon:
                tuples.append([name, monster_data.get("code", ""), i])
                icon.append(i)
    return tuples

def crop_to_content(pil_img):
    # PIL → OpenCV
    img = np.array(pil_img)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # Maske: Alles was nicht schwarz ist (>10)
    _, thresh = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)

    # Umrandung (Bounding Box)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        print("nothing to crop")
        return pil_img  # nichts zu croppen
    x, y, w, h = cv2.boundingRect(np.vstack(contours))

    # Zuschnitt
    cropped_img = img[y:y+h, x:x+w]

    # OpenCV → PIL zurück
    return Image.fromarray(cropped_img)


if __name__ == "__main__":
    # get_all_monsters()
    # transform_data_to_monsters_json()
    # get_monster_code_name_tupels()
    get_screenshots_of_monsters()