"""
Generic functions needed across the codebase.
"""

import os
import csv

import src.constants


def get_box_files(logs_dir):

    box_filenames = []

    for fi in os.listdir(logs_dir):
        day_dir = os.path.join(logs_dir, fi)
        if os.path.isdir(day_dir):
            for gi in os.listdir(day_dir):
                day_file = os.path.join(day_dir, gi)
                if os.path.isfile(day_file) and day_file[-3:] == "TXT":
                    box_filenames.append(day_file)

    return box_filenames


def ensure_date_in_filenames(path_list):

    for fpath in path_list:
        lfpath = fpath.split("/")
        if lfpath[-1][:8].isdigit():
            continue

        lfpath[-1] = lfpath[-2] + "_" + lfpath[-1]
        newpath = os.path.join(os.sep, *lfpath)
        print("Renaming file", fpath, "to", newpath)
        os.rename(fpath, newpath)

def read_csv(filename):
    """Read CSV file and return a reader."""

    csv_file = open(filename, newline="",encoding="utf-8")
    line = csv_file.readline()
    csv_reader = csv.reader(csv_file, delimiter="\t")
    if "," in line:
        csv_reader = csv.reader(csv_file, delimiter=",")

    return csv_reader

def write_to_csv_file(filename, data):

    try:
        with open(filename, 'w', newline='', encoding="utf-8") as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',')
            for d in data:
                csv_writer.writerow(d)

    except FileNotFoundError:
        print("Couldn't open CSV file: %s", filename)
