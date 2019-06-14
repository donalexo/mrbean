import base64
import os
import time

import requests
from PIL import Image, ImageDraw

API_KEY = os.environ['API_KEY_FACE++']
API_SECRET = os.environ['API_SECRET_FACE++']


def b64_encode(b):
    return str(base64.b64encode(b))[2:-1]


def plot_landmarks(img_path, landmarks):
    im = Image.open(img_path)
    d = ImageDraw.Draw(im)
    for landmark_key, landmark_values in landmarks.items():
        for sub_landmark_key, sub_landmark_values in landmark_values.items():
            if 'radius' in sub_landmark_key:
                rad = sub_landmark_values
                center = landmark_values[landmark_key + '_pupil_center']
                x, y = center['x'], center['y']
                d.ellipse((x - rad, y - rad, x + rad, y + rad))
            else:
                d.point([sub_landmark_values['x'], sub_landmark_values['y']])
    im.save('{}_landmarks.jpg'.format(os.path.splitext(img_path)[0]))


def plot_rectangle(img_path, rectangle):
    im = Image.open(img_path)
    d = ImageDraw.Draw(im)
    width, top, left, height = \
        rectangle['width'], rectangle['top'], \
        rectangle['left'], rectangle['height']
    upper_left_corner = (left, top)
    upper_right_corner = (left + width, top)
    lower_left_corner = (left, top + height)
    lower_right_corner = (left + width, top + height)
    line_color = (255, 255, 255)
    d.line([upper_left_corner, upper_right_corner, lower_right_corner, lower_left_corner, upper_left_corner],
           fill=line_color, width=1)
    im.save('{}_face_detected.jpg'.format(os.path.splitext(img_path)[0]))
    im.crop((left + 1, top + 1, left + width, top + height)).save(
        '{}_cropped.jpg'.format(os.path.splitext(img_path)[0]))


with open('bean1.jpg', 'rb') as fp:
    bean1 = fp.read()

with open('bean2.jpg', 'rb') as fp:
    bean2 = fp.read()

res = requests.post(
    url='https://api-us.faceplusplus.com/facepp/v3/compare',
    data={
        'api_key': API_KEY,
        'api_secret': API_SECRET,
        'image_base64_1': b64_encode(bean1),
        'image_base64_2': b64_encode(bean2)
    }
)
res.raise_for_status()
res_json = res.json()

face1_rectangle = res_json['faces1'][0]['face_rectangle']
face2_rectangle = res_json['faces2'][0]['face_rectangle']
plot_rectangle('bean1.jpg', face1_rectangle)
plot_rectangle('bean2.jpg', face2_rectangle)

# Sleep short time between requests - API complains sometimes
time.sleep(1)
with open('bean1_cropped.jpg', 'rb') as fp:
    bean1_cropped = fp.read()

res = requests.post(
    url='https://api-us.faceplusplus.com/facepp/v1/face/thousandlandmark',
    data={
        'api_key': API_KEY,
        'api_secret': API_SECRET,
        'image_base64': b64_encode(bean1_cropped),
        'return_landmark': 'all'
    }
)
res.raise_for_status()
res_json = res.json()
plot_landmarks('bean1_cropped.jpg', res_json['face']['landmark'])

# Sleep short time between requests - API complains sometimes
time.sleep(1)

with open('bean2_cropped.jpg', 'rb') as fp:
    bean2_cropped = fp.read()

res = requests.post(
    url='https://api-us.faceplusplus.com/facepp/v1/face/thousandlandmark',
    data={
        'api_key': API_KEY,
        'api_secret': API_SECRET,
        'image_base64': b64_encode(bean2_cropped),
        'return_landmark': 'all'
    }
)
res.raise_for_status()
res_json = res.json()
plot_landmarks('bean2_cropped.jpg', res_json['face']['landmark'])
