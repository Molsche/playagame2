import cv2
import os
import random

import numpy as np


def remove_black_background(image):
    """Entfernt den schwarzen Hintergrund und erstellt eine Alphamaske."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 9, 255, cv2.THRESH_BINARY)
    mask = cv2.GaussianBlur(mask, (5, 5), 0)
    image = image.astype(np.float32)
    mask_f = mask.astype(np.float32) / 255.0
    image[..., 0] *= mask_f  # B
    image[..., 1] *= mask_f  # G
    image[..., 2] *= mask_f  # R
    image = np.clip(image, 0, 255).astype(np.uint8)
    b, g, r = cv2.split(image)
    rgba = [b, g, r, mask]
    return cv2.merge(rgba)

def remove_specific_background(image, bg_color=(11, 9, 9)):
    """Macht nur genau den Hintergrund in der angegebenen Farbe transparent."""
    # Erstelle eine Maske, wo RGB exakt (9,9,11) ist
    mask = cv2.inRange(image, np.array(bg_color), np.array(bg_color))

    # Invertiere Maske: Alles außer Hintergrund = 255
    alpha = cv2.bitwise_not(mask)

    # Füge den Alpha-Kanal hinzu
    b, g, r = cv2.split(image)
    rgba = cv2.merge([b, g, r, alpha])
    return rgba

def visualize_transparency(rgba_img):
    # Erzeuge einen hellgrauen Hintergrund
    background = np.full(rgba_img.shape, (200, 200, 200, 255), dtype=np.uint8)

    # Alpha-Maske normalisieren auf [0,1]
    alpha = rgba_img[:, :, 3] / 255.0
    alpha = alpha[:, :, np.newaxis]  # (H, W, 1)

    # Nur RGB mischen, Alpha ignorieren
    blended = rgba_img[:, :, :3] * alpha + background[:, :, :3] * (1 - alpha)
    blended = blended.astype(np.uint8)

    cv2.imshow("Transparency Preview", blended)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def overlay_monster_on_background(monster_rgba, background_bgr):
    """Legt das Monsterbild auf einen Hintergrund."""
    h_bg, w_bg, _ = background_bgr.shape
    h_m, w_m, _ = monster_rgba.shape

    # Skalierung falls nötig
    scale = min(w_bg / w_m * 1, h_bg / h_m * 1)
    # monster_rgba = cv2.resize(monster_rgba, (0, 0), fx=scale, fy=scale)
    h_m, w_m, _ = monster_rgba.shape

    # Zufällige Position auf dem Hintergrund
    x = random.randint(0, w_bg - w_m)
    y = random.randint(0, h_bg - h_m)

    # RGBA in BGRA
    b, g, r, a = cv2.split(monster_rgba)
    monster_bgr = cv2.merge((b, g, r))

    roi = background_bgr[y:y + h_m, x:x + w_m]
    mask_inv = cv2.bitwise_not(a)

    bg_cut = cv2.bitwise_and(roi, roi, mask=mask_inv)
    fg_cut = cv2.bitwise_and(monster_bgr, monster_bgr, mask=a)

    combined = cv2.add(bg_cut, fg_cut)
    background_bgr[y:y + h_m, x:x + w_m] = combined

    return background_bgr

def generate_augmented_monster(monster_path, background_paths, output_path,i):
    """Erzeugt ein realistisches Trainingsbild mit Monster + Hintergrund."""
    monster_img = cv2.imread(monster_path)
    background_img = cv2.imread(random.choice(background_paths))

    monster_rgba = remove_specific_background(monster_img)
    composed_img = overlay_monster_on_background(monster_rgba, background_img)

    os.makedirs(output_path, exist_ok=True)
    out_name = os.path.join(output_path, f"composed_{i}.png")
    cv2.imwrite(out_name, composed_img)
    print(f"✓ Saved: {out_name}")


if __name__ == "__main__":
    monsters = [f.path for f in os.scandir("data/monster_images/mtpunjai1/val")]
    backgrounds = [f.path for f in os.scandir("data/images/backgrounds")]
    print(backgrounds)
    print(monsters)
    i = 0
    for m in monsters:
        generate_augmented_monster(m, backgrounds, "data/images/composed", i)
        i += 1
