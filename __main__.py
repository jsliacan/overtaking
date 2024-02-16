"""
Script utilizing code in overtaking package
"""

#! /usr/bin/python3

from collections import Counter

import csv
import os
import ast
import json

import matplotlib.pyplot as plt

from src import box, constants, radar, util


# --------- Scripting --------

# ------------
# treat lat. distances that are too small to be realistic
my_events = box.read_events_from_csvfile("data/events.csv")
ot_events = [e for e in my_events if e[0] == 1]
extreme_ot_events = [e for e in ot_events if min(e[-1])<100]

filtered_ot_events = []
for e in extreme_ot_events:
    # remove all entries <40cm
    while(min(e[-1]) < 40):
        e[-1].remove(min(e[-1]))
    # remove anomalies
    ldl = e[-1]
    for i in range(len(ldl)):
        try:
            if ldl[i] < ldl[i-1] - 50 and ldl[i] < ldl[i+1] - 50:
                e[-1].remove(e[-1][i])
        except:
            continue

    filtered_ot_events.append(e)

for e in [e for e in filtered_ot_events if min(e[-1]) < 100]:
    print(e)
print(len([e for e in filtered_ot_events if min(e[-1]) < 100]))




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

# -------------------------- TEST box.py ----------------------------
# extract events from the data
my_events = box.collate_events()
util.write_to_csv_file("data/events.csv", my_events)

# plot hist of minimum overtaking distances (one for each identified event)
min_overtaking_dist = []
min_oncoming_dist = []
for event in my_events[1:]:
    if event[0] == 1:
        min_overtaking_dist.append(min(event[-1]))
    elif event[0] == -1:
        min_oncoming_dist.append(min(event[-1]))

plt.hist(min_overtaking_dist, alpha=0.5, label='overtaking', bins=50)
plt.hist(min_oncoming_dist, alpha=0.5, label='oncoming', bins=50)
plt.legend(loc='upper right')
plt.savefig("figures/OT-vs-OC_events-hist.png")

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
