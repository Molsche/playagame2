import os
import time
import io
import csv
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from PIL import Image


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
