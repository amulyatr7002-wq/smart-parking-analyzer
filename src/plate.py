import re
import cv2
import numpy as np

try:
    import easyocr
except ImportError:
    easyocr = None


class PlateRecognizer:
    """
    Generic OCR-based plate reader.

    This first crops the lower/central vehicle region and asks EasyOCR
    for alphanumeric text. For a production Indian-number-plate system,
    use a dedicated plate detector before OCR.
    """

    def __init__(self):
        self.reader = None
        if easyocr is not None:
            self.reader = easyocr.Reader(["en"], gpu=False)

    @staticmethod
    def clean(text):
        text = re.sub(r"[^A-Za-z0-9]", "", text).upper()
        return text

    def read_vehicle(self, frame, bbox):
        if self.reader is None:
            return None

        h, w = frame.shape[:2]
        x1, y1, x2, y2 = map(int, bbox)

        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(w, x2)
        y2 = min(h, y2)

        crop = frame[y1:y2, x1:x2]
        if crop.size == 0:
            return None

        # Enlarge for OCR.
        crop = cv2.resize(crop, None, fx=2.5, fy=2.5,
                           interpolation=cv2.INTER_CUBIC)

        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 7, 50, 50)

        results = self.reader.readtext(gray, detail=1)
        candidates = []

        for _, text, conf in results:
            cleaned = self.clean(text)
            if len(cleaned) >= 5:
                candidates.append((cleaned, float(conf)))

        if not candidates:
            return None

        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0]
