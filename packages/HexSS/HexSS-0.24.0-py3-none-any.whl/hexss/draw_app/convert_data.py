from hexss.constants import *
from hexss import json_load
from hexss.image import controller
import os
import cv2
import random
import shutil

folder_path = "datasets"
if folder_path in os.listdir():
    shutil.rmtree(folder_path)

os.makedirs('datasets/train/images', exist_ok=True)
os.makedirs('datasets/valid/images', exist_ok=True)
os.makedirs('datasets/test/images', exist_ok=True)
os.makedirs('datasets/train/labels', exist_ok=True)
os.makedirs('datasets/valid/labels', exist_ok=True)
os.makedirs('datasets/test/labels', exist_ok=True)

img_folder = 'data2'
for folder_data_name in os.listdir(img_folder):
    if '.json' in folder_data_name:
        continue
    print(f'{CYAN}folder_data_name {folder_data_name}{END}')

    rect_frames = json_load(f'{img_folder}/{folder_data_name}.json')  # change name folde
    print(rect_frames)
    for img_name, rects in rect_frames.items():
        print(img_name)
        img = cv2.imread(f'{img_folder}/{folder_data_name}/{img_name}')  # change name folde

        txt = ''
        for name, rect in rects.items():
            x, y, w, h = rect['xywh']
            group = rect['group']
            txt += f'{group} {x} {y} {w} {h}\n'

        for brightness in [-10, -5, 0, 5, 10]:
            for contrast in [-10, -5, 0, 5, 10]:
                img2 = controller(img, brightness, contrast)

                path = random.choice([*['datasets/train'] * 75, *['datasets/valid'] * 20, *['datasets/test'] * 5])

                image_path = os.path.join(path, 'images')
                label_path = os.path.join(path, 'labels')

                cv2.imwrite(os.path.join(image_path, f'{img_name}{brightness}{contrast}.jpg'), img)
                with open(os.path.join(label_path, f'{img_name}{brightness}{contrast}.txt'), 'w') as f:
                    f.write(txt)
