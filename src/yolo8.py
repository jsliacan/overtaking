#!/usr/env/python

from ultralytics import YOLO
from PIL import Image
import cv2
import os
import pandas as pd

in_folder = "../data/trainingPix"
out_folder = "out"
model = YOLO("../models/yolov8x.pt")  # load a pretrained model (xlarge) from ultralytics (YOLOv8)

yolo_labels = {0: 'person', 1: 'bicycle', 2: 'car', 3: 'motorcycle', 4: 'airplane', 5: 'bus', 6: 'train', 7: 'truck', 8: 'boat', 9: 'traffic light', 10: 'fire hydrant', 11: 'stop sign', 12: 'parking meter', 13: 'bench', 14: 'bird', 15: 'cat', 16: 'dog', 17: 'horse', 18: 'sheep', 19: 'cow', 20: 'elephant', 21: 'bear', 22: 'zebra', 23: 'giraffe', 24: 'backpack', 25: 'umbrella', 26: 'handbag', 27: 'tie', 28: 'suitcase', 29: 'frisbee', 30: 'skis', 31: 'snowboard', 32: 'sports ball', 33: 'kite', 34: 'baseball bat', 35: 'baseball glove', 36: 'skateboard', 37: 'surfboard', 38: 'tennis racket', 39: 'bottle', 40: 'wine glass', 41: 'cup', 42: 'fork', 43: 'knife', 44: 'spoon', 45: 'bowl', 46: 'banana', 47: 'apple', 48: 'sandwich', 49: 'orange', 50: 'broccoli', 51: 'carrot', 52: 'hot dog', 53: 'pizza', 54: 'donut', 55: 'cake', 56: 'chair', 57: 'couch', 58: 'potted plant', 59: 'bed', 60: 'dining table', 61: 'toilet', 62: 'tv', 63: 'laptop', 64: 'mouse', 65: 'remote', 66: 'keyboard', 67: 'cell phone', 68: 'microwave', 69: 'oven', 70: 'toaster', 71: 'sink', 72: 'refrigerator', 73: 'book', 74: 'clock', 75: 'vase', 76: 'scissors', 77: 'teddy bear', 78: 'hair drier', 79: 'toothbrush'}

# our_labels = {2: 'car', 3: 'motorcycle', 5: 'bus', 6: 'train', 7: 'truck'}

# https://docs.ultralytics.com/modes/predict/#inference-arguments
results = model.predict(source=in_folder, save=True, save_conf=True, project=out_folder, name="annotated_pics", classes=[2,3,5,6,7])

lst = []
print("num results:", len(results))
for result in results:
    boxes = result.boxes.cpu().numpy()
    for box in boxes:
        cls = int(box.cls[0])
        path = result.path
        class_name = yolo_labels[cls]
        conf = int(box.conf[0]*100)
        bx = box.xywh.tolist()
        df = pd.DataFrame({'class_name': class_name, 'class_id': cls, 'confidence': conf, 'box_coord': bx, 'path': path})
        lst.append(df)
df = pd.concat(lst)
# Save the predicted text file to disk
df.to_csv(os.path.join(out_folder,"predicted_labels.csv"), index=False)
os.rename(os.path.join(out_folder,"predicted_labels.csv"), os.path.join("..", "data", "predicted_labels.csv"))

# with open("../data/predictions.txt", 'w') as file:
#     for prediction in results.xyxy[0]:
#         file.write(f"{prediction[0].item()} {prediction[1].item()} {prediction[2].item()} {prediction[3].item()}\n")
