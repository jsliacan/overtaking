import os
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


if __name__ == "__main__":

    print(get_box_files(constants.DATA_HOME))
