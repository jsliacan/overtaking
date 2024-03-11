"""
Script utilizing code in overtaking package

"""

#! /usr/bin/python3



"""
# --------- vehicle recognition from video ----------

import os
from ultralytics import YOLO
import pandas as pd

from src import detect


IN_FOLDER = "data/trainingPix"
OUT_FOLDER = "out"
model = YOLO("models/yolov8x.pt")  # load a pretrained model (xlarge) from ultralytics (YOLOv8)

YOLO_LABELS = {0: 'person', 1: 'bicycle', 2: 'car', 3: 'motorcycle', 4: 'airplane', 5: 'bus', 6: 'train', 7: 'truck', 8: 'boat', 9: 'traffic light', 10: 'fire hydrant', 11: 'stop sign', 12: 'parking meter', 13: 'bench', 14: 'bird', 15: 'cat', 16: 'dog', 17: 'horse', 18: 'sheep', 19: 'cow', 20: 'elephant', 21: 'bear', 22: 'zebra', 23: 'giraffe', 24: 'backpack', 25: 'umbrella', 26: 'handbag', 27: 'tie', 28: 'suitcase', 29: 'frisbee', 30: 'skis', 31: 'snowboard', 32: 'sports ball', 33: 'kite', 34: 'baseball bat', 35: 'baseball glove', 36: 'skateboard', 37: 'surfboard', 38: 'tennis racket', 39: 'bottle', 40: 'wine glass', 41: 'cup', 42: 'fork', 43: 'knife', 44: 'spoon', 45: 'bowl', 46: 'banana', 47: 'apple', 48: 'sandwich', 49: 'orange', 50: 'broccoli', 51: 'carrot', 52: 'hot dog', 53: 'pizza', 54: 'donut', 55: 'cake', 56: 'chair', 57: 'couch', 58: 'potted plant', 59: 'bed', 60: 'dining table', 61: 'toilet', 62: 'tv', 63: 'laptop', 64: 'mouse', 65: 'remote', 66: 'keyboard', 67: 'cell phone', 68: 'microwave', 69: 'oven', 70: 'toaster', 71: 'sink', 72: 'refrigerator', 73: 'book', 74: 'clock', 75: 'vase', 76: 'scissors', 77: 'teddy bear', 78: 'hair drier', 79: 'toothbrush'}

# our_labels = {2: 'car', 3: 'motorcycle', 5: 'bus', 6: 'train', 7: 'truck'}

# https://docs.ultralytics.com/modes/predict/#inference-arguments
results = model.predict(source=IN_FOLDER, save=True, save_conf=True, project=OUT_FOLDER, name="annotated_pics", classes=[2,3,5,6,7])

gt_box = [356.90081787109375, 509.1054992675781, 590.26416015625, 710.7196655273438]
lst = []

print("num results:", len(results))

for result in results:
    boxes = result.boxes.cpu().numpy()
    for box in boxes:
        cls = int(box.cls[0])
        path = result.path
        class_name = YOLO_LABELS[cls]
        conf = int(box.conf[0]*100)
        # 'xyxy': boxes are represented via corners, x1, y1 being top left and x2, y2 being bottom right
        # 'xywh' : boxes are represented via corner, width and height, x1, y2 being top left, w, h being width and height.
        # 'cxcywh' : boxes are represented via centre, width and height, cx, cy being center of box, w, h being width and height.
        bx = box.xyxy.tolist()
        mudguard = 0
        print(bx, gt_box)
        if detect.IoU(bx[0], gt_box) > 0.5:
            mudguard = 1
        df = pd.DataFrame({'mudguard': mudguard, 'class_name': class_name, 'class_id': cls, 'confidence': conf, 'box_coord': bx, 'path': path})
        lst.append(df)
df = pd.concat(lst)

# Save the predicted text file to disk
df.to_csv(os.path.join(OUT_FOLDER,"predicted_labels.csv"), index=False)
os.rename(os.path.join(OUT_FOLDER,"predicted_labels.csv"), os.path.join("data", "predicted_labels.csv"))
"""

# --------------- solve 1-entry overtakes --------------
import os
from src import box, util

#my_events = box.collate_events()
#util.write_to_csv_file(os.path.join("data", "events.csv"), my_events)

my_events = box.read_events_from_csvfile("data/events.csv")
ot_events = [e for e in my_events if e[0] == 1] # overtaking only
singular_ot_events = [e for e in ot_events if len(e[-1]) == 1] # overtaking of length 1
singular_events = [e for e in my_events if len(e[-1]) == 1] # overtaking of length 1
press_length_9 = [e for e in my_events if e[2] == 9]

for e in ot_events:
    if e[3] == 20240309:
        print(e)
        
#print("OT events of length 1:", len(singular_ot_events))
#print("OT events with non-zero flag:", len([e for e in ot_events if e[1] > 0]))

"""
# --------------- code related to the box --------------
from collections import Counter

import csv
import os
import ast
import json

import matplotlib.pyplot as plt
import networkx as nx

from src import box, constants, radar, util, detect


# ------------
# address lat. distances that are too small, e.g. in the following event
# d = [510, 203, 205, 134, 200, 200, 200, 198, 195, 195, 78, 195, 195, 193, 60, 40, 129, 193, 193, 144, 198, 195, 116, 195, 195, 195, 160, 195, 152]

# IDEA: convert the list to a graph: each lat dist is a vertex. If two
# vertices are close to each other (e.g. <40cm), add an edge between
# them. Then detect a community with Lovain algorithm based on
# modularity measure. Keep the biggest component.

my_events = box.read_events_from_csvfile("data/events.csv")
ot_events = [e for e in my_events if e[0] == 1] # overtaking only

k = 0
skipped = 0
skipped_edges = 0
min_overtaking_dist = []

for event in ot_events:
    distances = event[-1] # list of lat. distances for that event
    # print(".", end='', flush=True)
    if len(distances) == 1:
        print(event)
        # louvain can't handle 1 vertex graph
        skipped += 1
        k += 1
        continue
    nodes = range(len(distances))
    G = nx.Graph()
    G.add_nodes_from(nodes)

    for i in nodes:
        for j in nodes:
            # self-loops mess it up
            if i != j and abs(distances[i] - distances[j]) < 40:
                   G.add_edge(i,j)
    if len(G.edges()) == 0:
        # can't divide by 0
        skipped_edges += 1
        k += 1
        continue
    c = nx.community.louvain_communities(G)
    lengths_c = [len(x) for x in c]
    ix = lengths_c.index(max(lengths_c))
    dists = []
    nds = []
    for i in c[ix]:
        dists.append(distances[i])
        nds.append(i)
    min_overtaking_dist.append(min(dists))
#plt.hist(min_overtaking_dist, alpha=0.5, label='overtaking', bins=50)
#plt.savefig("figures/OT_filtered_events-hist.png")

    # generate scatter plots for each OT event highlighting the lat.dist. values we keep
    plt.scatter(nodes, distances, c='b')
    plt.scatter(nds, dists, c='r')
    plt.ylim([100,500])
    plt.savefig(os.path.join("out", "figs", str(event[3])+"_"+str(event[4])+"_"+str(event[5])+".png"))
    plt.clf()
    k += 1
print()
print("skipped:", skipped)
print("skipped (no edges):", skipped_edges)
print("total:", k)
min_overtaking_dist.sort()
print("min OT distances for each event, sorted:\n", min_overtaking_dist)
"""
"""
# ----------------- press lengths --------------
# Load or compile tally of press lengths (bin size = 1)
PRESSES_JSON = "data/press_lengths_counts.json"
PRESSES_PNG = "figures/press_lengths_hist.png"

# Create a tally of press lengths
# (to see if there is a clear distinction between short and long presses)
if os.path.exists(PRESSES_JSON):
    print("Using press lengths (historgram) from: ", PRESSES_JSON)
    with open(PRESSES_JSON, encoding="utf-8") as f:
        data = f.read()
    d = ast.literal_eval(data)
    print(d)
else:
    print("File ", PRESSES_JSON, "does not exit. Compiling info and creating the file.")
    my_events = box.collate_events()
    press_lengths = [event[2] for event in my_events[1:]] # press length sits at index 2 in an event
    c = Counter(press_lengths)
    with open(PRESSES_JSON, "w", encoding="utf-8") as outfile:
        json.dump(c, outfile)

    # while at it, generate the Figure with histogram
    plt.hist(press_lengths, bins=range(1,max(press_lengths)), label='press lengths')
    plt.legend(loc='upper right')
    plt.savefig(PRESSES_PNG)

my_events = box.collate_events()
for event in my_events:
    print(event)
print("Found", len(my_events), "events.")
"""
"""
# -------------------------- TEST box.py ----------------------------
# extract events from the data
import os
from src import box, util


# [1, 2, 9, 20230112, '19:48:17', 94962, 1, [365]]
# [1, 4, 29, 20221227, '14:33:53', 387031, 1, [243]]
# [1, 0, 28, 20221224, '11:02:56', 123439, 1, [144]]
# [1, 1, 9, 20221218, '09:29:42', 2104, 1, [370]]
# [1, 0, 37, 20230119, '08:58:13', 155376, 1, [462]]
# [1, 3, 8, 20230219, '10:05:38', 164892, 1, [368]]
# [1, 3, 9, 20230219, '10:42:52', 211805, 1, [485]]
# [1, 0, 31, 20230219, '12:59:49', 384818, 1, [71]]
# [1, 3, 8, 20230305, '09:01:37', 168094, 1, [386]]
# [1, 0, 38, 20230318, '12:08:04', 95322, 1, [91]]
# [1, 0, 38, 20230318, '12:42:53', 139226, 1, [106]]

my_events = box.collate_events()
util.write_to_csv_file(os.path.join("data", "events.csv"), my_events)

for event in my_events:
    if event[-2] == 0:
        print(event)
# plot hist of minimum overtaking distances (one for each identified event)
# min_overtaking_dist = []
# min_oncoming_dist = []
# for event in my_events[1:]:
#     if event[0] == 1:
#         min_overtaking_dist.append(min(event[-1]))
#     elif event[0] == -1:
#         min_oncoming_dist.append(min(event[-1]))

# plt.hist(min_overtaking_dist, alpha=0.5, label='overtaking', bins=50)
# plt.hist(min_oncoming_dist, alpha=0.5, label='oncoming', bins=50)
# plt.legend(loc='upper right')
# plt.savefig("figures/OT-vs-OC_events-hist.png")
"""
"""
# -------------------------- TEST radar.py ----------------------------
radar.radar_decode()

# -------------------------- TEST util.py ----------------------------

for f in util.get_box_files(constants.DATA_HOME):
    print(f)

print()
util.ensure_date_in_filenames(util.get_box_files(constants.DATA_HOME))

print("Added date to filenames whenever it was missing:")

for f in util.get_box_files(constants.DATA_HOME):
    print(f)
"""
