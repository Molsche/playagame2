import cv2
import torch

from WindowExtractor import get_img_in_RGB


class YoloEye:
    def __init__(self, region=str, model=str):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = torch.hub.load('ultralytics/yolov5', model, pretrained=True).to(self.device)
        self.region = region
        self.detections = None
        self.img = None
        self.model.eval()

    def run_yolo_detection(self):
        # Convert to RGB and prepare image for YOLO
        self.img = get_img_in_RGB(self.region)
        results = self.model(self.img)

        # Parse results
        detections = results.xyxy[0].cpu().numpy()  # x1, y1, x2, y2, conf, class
        labels = results.names

        parsed = []
        for *xyxy, conf, cls_id in detections:
            label = labels[int(cls_id)]
            parsed.append({
                "label": label,
                "confidence": round(float(conf), 2),
                "box": list(map(int, xyxy))
            })
        self.detections = parsed
        self.draw_yolo_detections_on_img()
        return self.detections

    def draw_yolo_detections_on_img(self):
        """
        Draws bounding boxes and labels from YOLO detections on the image and displays it.

        Args:
            detections (list): List of dicts with keys 'label', 'confidence', 'box'
            img (ndarray): BGR image as a NumPy array (e.g., from cv2 or mss)
        """
        for det in self.detections:
            label = det['label']
            conf = det['confidence']
            x1, y1, x2, y2 = det['box']

            # Draw rectangle
            cv2.rectangle(self.img, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Draw label text
            text = f"{label} {conf:.2f}"
            (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
            cv2.rectangle(self.img, (x1, y1 - text_height - 5), (x1 + text_width, y1), (0, 255, 0), -1)
            cv2.putText(self.img, text, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)

        # Show image
        cv2.imshow("YOLO Detections", self.img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()