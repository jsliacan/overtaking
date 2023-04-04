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


def ensure_date_in_filenames(path_list):

    for fpath in path_list:
        lfpath = fpath.split("/")
        if lfpath[-1][:8].isdigit():
            continue
        else:
            lfpath[-1] = lfpath[-2] + "_" + lfpath[-1]
            newpath = os.path.join(lfpath)
            print("Renaming file", fpath, "to", newpath)
            os.rename(fpath, newpath)


if __name__ == "__main__":

    for f in get_box_files(constants.DATA_HOME):
        print(f)

    print()
    ensure_date_in_filenames(get_box_files(constants.DATA_HOME))

    print("Added date to filenames whenever it was missing:")

    for f in get_box_files(constants.DATA_HOME):
        print(f)
