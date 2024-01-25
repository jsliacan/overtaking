"""
Script analyzing button press lengths.
"""

#! /usr/bin/python3

from collections import Counter

import os
import ast
import json

import matplotlib.pyplot as plt

import box
import util

# Load or compile tally of press lengths (bin size = 1)
PRESSES_JSON = "data/press_lengths_counts.json"
PRESSES_PNG = "figures/press_lengths_hist.png"

if os.path.exists(PRESSES_JSON):
    print("Using press lengths (historgram) from: ", PRESSES_JSON)
    with open(PRESSES_JSON) as f:
        data = f.read()
    d = ast.literal_eval(data)
    print(d)
else:
    print("File ", PRESSES_JSON, "does not exit. Compiling info and creating the file.")
    my_events = box.collate_events()
    press_lengths = [event[2] for event in my_events[1:]] # press length sits at index 2 in an event
    c = Counter(press_lengths)
    with open(PRESSES_JSON, "w") as outfile:
        json.dump(c, outfile)

    # while at it, generate the Figure with histogram
    plt.hist(press_lengths, bins=range(1,max(press_lengths)), label='press lengths')
    plt.legend(loc='upper right')
    plt.savefig(PRESSES_PNG)

