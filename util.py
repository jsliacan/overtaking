import os
import csv

import constants


def get_box_files(logs_dir):

    box_filenames = []

    for f in os.listdir(logs_dir):
        day_dir = os.path.join(logs_dir, f)
        if os.path.isdir(day_dir):
            for g in os.listdir(day_dir):
                day_file = os.path.join(day_dir, g)
                if os.path.isfile(day_file) and day_file[-3:] == "TXT":
                    box_filenames.append(day_file)

    return box_filenames


def ensure_date_in_filenames(path_list):

    for fpath in path_list:
        lfpath = fpath.split("/")
        if lfpath[-1][:8].isdigit():
            continue
        else:
            lfpath[-1] = lfpath[-2] + "_" + lfpath[-1]
            newpath = os.path.join(os.sep, *lfpath)
            print("Renaming file", fpath, "to", newpath)
            os.rename(fpath, newpath)

def read_csv(filename):
    """Read CSV file and return a reader."""
    csv_file = open(filename, newline="")

    line = csv_file.readline()
    csv_reader = csv.reader(csv_file, delimiter="\t")
    if "," in line:
        csv_reader = csv.reader(csv_file, delimiter=",")

    return csv_reader

def write_to_csv_file(filename, data):

    try:
        with open(filename, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=',')
            for d in data:
                csvwriter.writerow(d)
            
    except FileNotFoundError:
        print("Couldn't open CSV file: %s", filename)

        
if __name__ == "__main__":

    for f in get_box_files(constants.DATA_HOME):
        print(f)

    print()
    ensure_date_in_filenames(get_box_files(constants.DATA_HOME))

    print("Added date to filenames whenever it was missing:")

    for f in get_box_files(constants.DATA_HOME):
        print(f)
