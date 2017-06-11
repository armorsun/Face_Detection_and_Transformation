import json
from PIL import Image, ImageDraw, ImageFont
import os
import json
import math as m
from matplotlib import pyplot as plt
import numpy as np

result_path = 'face_detection_result/'
img_path = 'psy_faces'
radius = 1

images = {'east_man': [], 'east_woman': [], 'west_woman': [], 'west_man': []}
for img in os.listdir(result_path):
    if img.endswith('.json'):
        if 'em' in img:
            images['east_man'].append(img)
        elif 'ef' in img:
            images['east_woman'].append(img)
        elif 'wf' in img:
            images['west_woman'].append(img)
        elif 'wm' in img:
            images['west_man'].append(img)

face_parameters = {'east_man': {'individual':{}}, 'east_woman': {'individual':{}}, 'west_woman': {'individual':{}}, 'west_man': {'individual':{}}}

for categories in images:
    sum_eye_length_eye2nose = 0
    sum_mouth2nose_eye2nose = 0
    sum_pupil2nose_eye2nose = 0
    sum_eye2mouth_eye2nose = 0
    img_num = len(images[categories])
    print('There are %(1)s images in %(2)s' % {'1': img_num, '2': categories})

    for data in images[categories]:
        with open(os.path.join(result_path, data)) as json_file:
            markers = json.load(json_file)
            eye_length = 0
            mouth2nose = 0
            eye2nose = 0
            eye2mouth = 0

            try:
                eye_length = m.sqrt(m.pow((markers['faces'][0]['landmark']['right_eye_pupil']['x']
                                           - markers['faces'][0]['landmark']['left_eye_pupil']['x']), 2)
                                    + m.pow((markers['faces'][0]['landmark']['right_eye_pupil']['y']
                                             - markers['faces'][0]['landmark']['left_eye_pupil']['y']), 2))

                eye_middle = [(markers['faces'][0]['landmark']['right_eye_pupil']['x'] +
                               markers['faces'][0]['landmark']['left_eye_pupil']['x']) / 2,
                              (markers['faces'][0]['landmark']['right_eye_pupil']['y'] +
                               markers['faces'][0]['landmark']['left_eye_pupil']['y']) / 2]

                mouth = [(markers['faces'][0]['landmark']['mouth_upper_lip_top']['x'] +
                          markers['faces'][0]['landmark']['mouth_lower_lip_bottom']['x']) / 2,
                         (markers['faces'][0]['landmark']['mouth_upper_lip_top']['y'] +
                          markers['faces'][0]['landmark']['mouth_lower_lip_bottom']['y']) / 2]

                pupil2nose = m.sqrt(m.pow((markers['faces'][0]['landmark']['right_eye_pupil']['x']
                                         - markers['faces'][0]['landmark']['nose_tip']['x']), 2)
                                  + m.pow((markers['faces'][0]['landmark']['right_eye_pupil']['y']
                                         - markers['faces'][0]['landmark']['nose_tip']['y']), 2))

                nose = [markers['faces'][0]['landmark']['nose_tip']['x'], markers['faces'][0]['landmark']['nose_tip']['y']]

                eye2nose = m.sqrt(m.pow(nose[0] - eye_middle[0], 2) + m.pow(nose[1] - eye_middle[1], 2))
                eye2mouth = m.sqrt(m.pow(mouth[0] - eye_middle[0], 2) + m.pow(mouth[1] - eye_middle[1], 2))
                mouth2nose = m.sqrt(m.pow(mouth[0] - nose[0], 2) + m.pow(mouth[1] - nose[1], 2))

                eye_length_eye2nose = eye_length / eye2nose
                mouth2nose_eye2nose = mouth2nose / eye2nose
                pupil2nose_eye2nose = pupil2nose / eye2nose
                eye2mouth_eye2nose = eye2mouth / eye2nose

                sum_eye_length_eye2nose = sum_eye_length_eye2nose + eye_length_eye2nose
                sum_mouth2nose_eye2nose = sum_mouth2nose_eye2nose + mouth2nose_eye2nose
                sum_pupil2nose_eye2nose = sum_pupil2nose_eye2nose + pupil2nose_eye2nose
                sum_eye2mouth_eye2nose = sum_eye2mouth_eye2nose + eye2mouth_eye2nose

                face_parameters[categories]['individual'][data] = {'eye_length_eye2nose': eye_length_eye2nose,
                                                                   'mouth2nose_eye2nose': mouth2nose_eye2nose,
                                                                   'pupil2nose_eye2nose': pupil2nose_eye2nose,
                                                                   'eye2mouth_eye2nose': eye2mouth_eye2nose }

                img = Image.open(os.path.join(img_path, categories, data.replace('.json', '')))
                draw = ImageDraw.Draw(img)

                landmarks = markers['faces'][0]['landmark']
                for landmark in landmarks:
                    draw.ellipse([landmarks[landmark]['x'] - radius, landmarks[landmark]['y'] - radius,
                                  landmarks[landmark]['x'] + radius, landmarks[landmark]['y'] + radius], fill='red')

                draw.ellipse([eye_middle[0] - radius, eye_middle[1] - radius,
                              eye_middle[0] + radius, eye_middle[1] + radius], fill='blue')

                draw.ellipse([nose[0] - radius, nose[1] - radius,
                              nose[0] + radius, nose[1] + radius], fill='blue')

                draw.ellipse([mouth[0] - radius, mouth[1] - radius,
                              mouth[0] + radius, mouth[1] + radius], fill='blue')

                draw.ellipse([markers['faces'][0]['landmark']['right_eye_pupil']['x'] - radius, markers['faces'][0]['landmark']['right_eye_pupil']['y'] - radius,
                              markers['faces'][0]['landmark']['right_eye_pupil']['x'] + radius, markers['faces'][0]['landmark']['right_eye_pupil']['y'] + radius], fill='blue')

                draw.line([(eye_middle[0], eye_middle[1]), (nose[0], nose[1])], fill=(57, 239, 236, 220), width=2)
                draw.line([(mouth[0], mouth[1]), (nose[0], nose[1])], fill=(57, 239, 236, 220), width=2)
                draw.line([(mouth[0], mouth[1]), (eye_middle[0], eye_middle[1])], fill=(148, 98, 229, 220), width=2)
                draw.line([(markers['faces'][0]['landmark']['right_eye_pupil']['x'], markers['faces'][0]['landmark']['right_eye_pupil']['y']), (nose[0], nose[1])], fill=(57, 239, 236, 220), width=2)
                draw.line([(markers['faces'][0]['landmark']['right_eye_pupil']['x'], markers['faces'][0]['landmark']['right_eye_pupil']['y']),
                           (markers['faces'][0]['landmark']['left_eye_pupil']['x'], markers['faces'][0]['landmark']['left_eye_pupil']['y'])], fill=(57, 239, 236, 220), width=2)

                draw.text((10, 10), "eye_length_eye2nose " + str("{:.2f}".format(eye_length_eye2nose)), (0, 220, 50, 180), font=ImageFont.truetype("Arial.ttf", 18))
                draw.text((10, 30), "mouth2nose_eye2nose " + str("{:.2f}".format(mouth2nose_eye2nose)), (0, 220, 50, 180), font=ImageFont.truetype("Arial.ttf", 18))
                draw.text((10, 50), "pupil2nose_eye2nose " + str("{:.2f}".format(pupil2nose_eye2nose)), (0, 220, 50, 180), font=ImageFont.truetype("Arial.ttf", 18))
                draw.text((10, 70), "eye2mouth_eye2nose " + str("{:.2f}".format(eye2mouth_eye2nose)), (0, 220, 50, 180), font=ImageFont.truetype("Arial.ttf", 18))

                img.save('faces_after_marked/' + data.replace('.jpg.json', '') + '_marked.jpg')

            except Exception:
                img_num = img_num - 1
                print('may not found faces on', json_file)
                pass

    face_parameters[categories]['avg_eye_length_eye2nose'] = sum_eye_length_eye2nose / img_num
    face_parameters[categories]['avg_mouth2nose_eye2nose'] = sum_mouth2nose_eye2nose / img_num
    face_parameters[categories]['avg_pupil2nose_eye2nose'] = sum_pupil2nose_eye2nose / img_num
    face_parameters[categories]['avg_eye2mouth_eye2nose'] = sum_eye2mouth_eye2nose / img_num

##plot
# N = 4
# bar_width = 0.15
# index = np.arange(N)
#
# nose = (1, 1, 1, 1)
# eye_length_eye2nose_mean = (face_parameters['east_man']['avg_eye_length_eye2nose'], face_parameters['east_woman']['avg_eye_length_eye2nose'],
#                             face_parameters['west_man']['avg_eye_length_eye2nose'], face_parameters['west_woman']['avg_eye_length_eye2nose'])
#
# mouth2nose_eye2nose_mean = (face_parameters['east_man']['avg_mouth2nose_eye2nose'], face_parameters['east_woman']['avg_mouth2nose_eye2nose'],
#                             face_parameters['west_man']['avg_mouth2nose_eye2nose'], face_parameters['west_woman']['avg_mouth2nose_eye2nose'])
#
# pupil2nose_eye2nose_mean = (face_parameters['east_man']['avg_pupil2nose_eye2nose'], face_parameters['east_woman']['avg_pupil2nose_eye2nose'],
#                             face_parameters['west_man']['avg_pupil2nose_eye2nose'], face_parameters['west_woman']['avg_pupil2nose_eye2nose'])
#
# eye2mouth_eye2nose_mean = (face_parameters['east_man']['avg_eye2mouth_eye2nose'], face_parameters['east_woman']['avg_eye2mouth_eye2nose'],
#                             face_parameters['west_man']['avg_eye2mouth_eye2nose'], face_parameters['west_woman']['avg_eye2mouth_eye2nose'])
#
# fig, ax = plt.subplots()
#
# rects_nose = ax.bar(index, nose, bar_width, color='#96D6F2')
# rects_mouth2nose_eye2nose = ax.bar(index + bar_width, mouth2nose_eye2nose_mean, bar_width, color='#FDEB6C')
# rects_pupil2nose_eye2nose = ax.bar(index + 2 * bar_width, pupil2nose_eye2nose_mean, bar_width, color='#F49992')
# rects_eye_length_eye2nose = ax.bar(index + 3 * bar_width, eye_length_eye2nose_mean, bar_width, color='#99E3BA')
# rects_eye2mouth_eye2nose = ax.bar(index + 4 * bar_width, eye2mouth_eye2nose_mean, bar_width, color='#CC78D6')

#plt.legend()
# plt.xticks(index + 2.5 * bar_width , ('east_man', 'east_woman', 'west_man', 'west_woman'))
#
# plt.savefig('face_analysis.png')

N = 4
bar_width = 0.15
index = np.arange(N)

east_man_avgs = (face_parameters['east_man']['avg_eye_length_eye2nose'], face_parameters['east_man']['avg_mouth2nose_eye2nose'],
                    face_parameters['east_man']['avg_pupil2nose_eye2nose'], face_parameters['east_man']['avg_eye2mouth_eye2nose'])

east_woman_avgs = (face_parameters['east_woman']['avg_eye_length_eye2nose'], face_parameters['east_woman']['avg_mouth2nose_eye2nose'],
                    face_parameters['east_woman']['avg_pupil2nose_eye2nose'], face_parameters['east_woman']['avg_eye2mouth_eye2nose'])

west_man_avgs = (face_parameters['west_man']['avg_eye_length_eye2nose'], face_parameters['west_man']['avg_mouth2nose_eye2nose'],
                    face_parameters['west_man']['avg_pupil2nose_eye2nose'], face_parameters['west_man']['avg_eye2mouth_eye2nose'])

west_woman_avgs = (face_parameters['west_woman']['avg_eye_length_eye2nose'], face_parameters['west_woman']['avg_mouth2nose_eye2nose'],
                    face_parameters['west_woman']['avg_pupil2nose_eye2nose'], face_parameters['west_woman']['avg_eye2mouth_eye2nose'])

fig, ax = plt.subplots()

rects_east_man_avgs = ax.bar(index + 1.5 * bar_width, east_man_avgs, bar_width, color='#FDEB6C')
rects_east_woman_avgs  = ax.bar(index + 2.5 * bar_width , east_woman_avgs, bar_width, color='#F49992')
rects_west_man_avgs = ax.bar(index + 3.5 * bar_width, west_man_avgs, bar_width, color='#99E3BA')
rects_west_woman_avgs = ax.bar(index + 4.5 * bar_width, west_woman_avgs, bar_width, color='#CC78D6')

plt.xticks(index + 3.5 * bar_width , ('eye_length', 'mouth2nose', 'pupil2nose', 'eye2mouth'))

plt.savefig('face_analysis.png')

##find the most similar face

for categories in images:
    avg_eye2mouth_eye2nose = face_parameters[categories]['avg_eye2mouth_eye2nose']
    avg_mouth2nose_eye2nose = face_parameters[categories]['avg_mouth2nose_eye2nose']
    avg_pupil2nose_eye2nose = face_parameters[categories]['avg_pupil2nose_eye2nose']
    avg_eye_length_eye2nose = face_parameters[categories]['avg_eye_length_eye2nose']
    diffs = {}

    for face in face_parameters[categories]['individual']:
        diff = (abs(face_parameters[categories]['individual'][face]['pupil2nose_eye2nose'] - avg_pupil2nose_eye2nose) +
                abs(face_parameters[categories]['individual'][face]['eye_length_eye2nose'] - avg_eye_length_eye2nose) +
                abs(face_parameters[categories]['individual'][face]['mouth2nose_eye2nose'] - avg_mouth2nose_eye2nose) +
                abs(face_parameters[categories]['individual'][face]['eye2mouth_eye2nose'] - avg_eye2mouth_eye2nose))

        diffs[face] = diff
        face_parameters[categories]['individual'][face]['diff_from_avg'] = diff

    min_face = min(diffs, key=diffs.get)
    face_parameters[categories]['min_diff'] = [min_face ,face_parameters[categories]['individual'][min_face]]

with open('face_parameters.json', 'w') as outfile:
    json.dump(face_parameters, outfile)

for categories in images:
    print(face_parameters[categories]['min_diff'])