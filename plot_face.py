import json
import argparse
from PIL import Image, ImageDraw
import os

path = 'face_detection_result/'

parser = argparse.ArgumentParser()
parser.add_argument("face_image_names", nargs='+', help="put variables contained face image names here")
args = parser.parse_args()
face_names = args.face_image_names
print str(len(face_names)) + ' images found: ', face_names

radius = 2

for name in face_names:
    img = Image.open(name + '.jpg')
    draw = ImageDraw.Draw(img)

    with open(os.path.join(path, name + '.json')) as json_data:
        data = json.load(json_data)
        landmarks = data['faces'][0]['landmark']
        for landmark in landmarks:
            draw.ellipse([landmarks[landmark]['x'] - radius, landmarks[landmark]['y'] - radius,
                          landmarks[landmark]['x'] + radius, landmarks[landmark]['y'] + radius], fill='blue')

    img.show()
    img.save('faces_after_marked/' + name + '_marked.jpg')


