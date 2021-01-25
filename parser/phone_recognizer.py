import cv2
import numpy as np
import base64
import pytesseract


def base64_image_to_text(uri, tesseract_cmd):
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    encoded_data = uri.split(',')[1]
    nparr = np.fromstring(base64.b64decode(encoded_data), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return pytesseract.image_to_string(img)
