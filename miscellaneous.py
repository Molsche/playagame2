import pygetwindow as gw
from mss import mss
import numpy as np
import cv2
import time
import os
import xml.etree.ElementTree as ET


def get_florensia_window_region():
    """
    Detect the window titled 'Florensia' and return its position and size
    as a region tuple: (left, top, width, height)
    """
    titles = gw.getAllTitles()
    print(titles)
    florensia_title = [title for title in titles if "Florensia" in title]
    print(florensia_title[0])
    florensia = None
    for w in gw.getWindowsWithTitle(florensia_title[0]):
        if w.visible:
            florensia = w
            break

    if not florensia:
        raise Exception("Florensia window not found!")

    left = florensia.left
    top = florensia.top
    width = florensia.width
    height = florensia.height

    return {"top": top, "left": left, "width": width, "height": height}


def capture_region(regions, save=False):
    sct = mss()
    for name, region in regions.items():
        img = np.array(sct.grab(region))

        if save:
            filename = f"data/screenshots/{name}_{int(time.time())}.png"
            cv2.imwrite(filename, img)
        else:
            cv2.imshow(f"{name}", img)
            input("Press Enter to continue...")
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()


def convert_VOC_to_YOLO_box(size, box):
    """Convert box from VOC to YOLO format"""
    dw = 1. / size[0]
    dh = 1. / size[1]
    x = (box[0] + box[2]) / 2.0
    y = (box[1] + box[3]) / 2.0
    w = box[2] - box[0]
    h = box[3] - box[1]
    return x * dw, y * dh, w * dw, h * dh

def convert_VOC_to_YOLO(input_dir, output_dir, CLASSES):
    for filename in os.listdir(input_dir):
        if not filename.endswith(".xml"):
            continue

        tree = ET.parse(os.path.join(input_dir, filename))
        root = tree.getroot()

        size = root.find("size")
        w = int(size.find("width").text)
        h = int(size.find("height").text)

        output_lines = []
        for obj in root.findall("object"):
            cls = obj.find("name").text
            if cls not in CLASSES:
                continue
            cls_id = CLASSES.index(cls)
            xml_box = obj.find("bndbox")
            box = (
                int(xml_box.find("xmin").text),
                int(xml_box.find("ymin").text),
                int(xml_box.find("xmax").text),
                int(xml_box.find("ymax").text),
            )
            bbox = convert_VOC_to_YOLO_box((w, h), box)
            output_lines.append(f"{cls_id} {' '.join(f'{a:.6f}' for a in bbox)}")

        label_filename = os.path.splitext(filename)[0] + ".txt"
        print(label_filename)
        with open((output_dir + "/" + label_filename), "w") as f:
            f.write("\n".join(output_lines))

def get_screenshot_of_whole_game(monitor, save, name):
    sct = mss()
    img = np.array(sct.grab(monitor))
    if save:
        filename = f"data/screenshots/{name}_{int(time.time())}.png"
        cv2.imwrite(filename, img)


def convert_voc_to_yolo_format(xml_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    class_set = set()

    for filename in os.listdir(xml_folder):
        if not filename.endswith(".xml"):
            continue

        xml_path = os.path.join(xml_folder, filename)
        tree = ET.parse(xml_path)
        root = tree.getroot()

        size = root.find("size")
        img_width = int(size.find("width").text)
        img_height = int(size.find("height").text)

        yolo_lines = []
        for obj in root.findall("object"):
            class_name = obj.find("name").text
            class_set.add(class_name)

            bndbox = obj.find("bndbox")
            xmin = int(bndbox.find("xmin").text)
            ymin = int(bndbox.find("ymin").text)
            xmax = int(bndbox.find("xmax").text)
            ymax = int(bndbox.find("ymax").text)

            # Convert to YOLO format
            x_center = ((xmin + xmax) / 2) / img_width
            y_center = ((ymin + ymax) / 2) / img_height
            width = (xmax - xmin) / img_width
            height = (ymax - ymin) / img_height

            # Placeholder class index (to be replaced after indexing)
            yolo_lines.append((class_name, f"{x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"))

        # Write .txt label file
        base_filename = os.path.splitext(filename)[0]
        output_txt_path = os.path.join(output_folder, base_filename + ".txt")

        with open(output_txt_path, "w") as f:
            for class_name, yolo_line in yolo_lines:
                class_index = sorted(class_set).index(class_name)
                f.write(f"{class_index} {yolo_line}\n")

    # Output the list of sorted classes
    sorted_classes = sorted(class_set)
    print("\nDetected Classes Array (in class ID order):")
    print(sorted_classes)
    return sorted_classes
#test

if __name__ == "__main__":
    import torch
    import torch_directml

    dml = torch_directml.device()
    a = torch.tensor([1.0, 2.0, 3.0], device=dml)
    b = torch.tensor([4.0, 5.0, 6.0], device=dml)
    print(a + b)
    # print("hello")
    # convert_voc_to_yolo_format("data/screenshots", "data/labels")
    # get_screenshot_of_whole_game(get_florensia_window_region(), True, "Florensia")