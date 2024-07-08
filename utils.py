import cv2
import numpy as np
import requests
from io import BytesIO
from PIL import Image, ImageOps

def load_image(source):
    if isinstance(source, str) and source.startswith('http'):
        response = requests.get(source)
        img = Image.open(BytesIO(response.content))
    else:
        img = Image.open(source)
    
    img_np = np.array(img)
    return img_np, img

def load_image_ktp(input_source):
    if isinstance(input_source, bytes):
        image = Image.open(BytesIO(input_source))
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    elif isinstance(input_source, str):
        if input_source.startswith('http://') or input_source.startswith('https://'):
            response = requests.get(input_source)
            image = Image.open(BytesIO(response.content))
            image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        else:
            image = cv2.imread(input_source)
    else:
        raise ValueError("Unsupported input type. Must be a file path, URL, or bytes.")
    return image

def calculate_rotation_angle(landmarks):
    left_eye = landmarks[36]
    right_eye = landmarks[45]
    delta_x = right_eye[0] - left_eye[0]
    delta_y = right_eye[1] - left_eye[1]
    angle = np.arctan2(delta_y, delta_x) * (180 / np.pi)
    return angle

def rotate_image(image, angle):
    return ImageOps.exif_transpose(image.rotate(-angle, expand=True))

def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')
