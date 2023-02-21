

import os
import csv
import constants

ldata = []  # will hold contents of the CSV file in list format


def get_first_minimum(seq):
    """Returns the first minimum int it encounters in the list seq."""
    fmin = seq[0]
    for t in seq:
        if t < fmin:
            fmin = t
        elif t > fmin*1.2:  # needs a robustness coeff so it doesn't end at a little fluctuation
            return fmin
    return fmin


def read_csv(filename):
    """Read CSV file and return a reader."""
    csv_file = open(filename, newline='')
    csv_reader = csv.reader(csv_file, delimiter=',')

    return csv_reader


def get_press_lengths_and_starts(ldata):

    press_lengths = list()
    press_starts = list()
    len_press = 0

    i = 0
    for row in ldata:

        if row[5] == 1:
            if len_press == 0:
                press_starts.append(i)
            len_press += 1

        if row[5] == 0 and len_press > 0:
            press_lengths.append(len_press)
            len_press = 0

        i += 1

    return (press_starts, press_lengths)


def correct_press_lengths_and_starts(press_starts, press_lengths):
    """
    Check if any presses are only <2 rows apart. If yes, concatenate those presses.

    It is physically near-impossible to press button 2x (on purpose) only 1/11s apart.
    """

    original_num_presses = len(press_starts)
    num_presses = original_num_presses
    offset = 2  # offset=1 is simply due to indexing from 0 to len-offset

    while True:
        for i in range(num_presses-offset):

            # if button presses are too close to each other
            if press_starts[i] + press_lengths[i] >= press_starts[i+1] - 2:
                # keep press_start of the first press
                # make its length sum of the two presses plus gap between them
                press_lengths[i] = press_starts[i+1] - \
                    press_starts[i] + press_lengths[i+1]
                press_lengths.pop(i+1)  # remove the second press
                press_starts.pop(i+1)  # remove the second press
                offset += 1

        if num_presses == original_num_presses:  # if no changes, done.
            break
        else:
            # if concatenated some presses, repeat.
            original_num_presses = num_presses

    return (press_starts, press_lengths)


def get_press_timestamps(ldata, press_starts):

    timestamps = []

    for es in press_starts:
        for j in range(22):  # there's a timestamp within every 22 rows
            timestamp = ldata[es+j][0].strip()
            if timestamp != "":
                timestamps.append(timestamp)
                break

    return timestamps


def make_ldata(csv_reader):

    ldata = list(csv_reader)
    for i in range(1, len(ldata)):
        ldata[i][4] = int(ldata[i][4].strip())
        ldata[i][5] = int(ldata[i][5].strip())

    return ldata


def find_passing_cars(ps, pl, ldata):
    """Returns a lit of before-intervals and after-intervals for each button press.

    INPUT:

    ps      - row where the button press starts in ldata
    pl      - length of the button press starting at row ps
    ldata   - csv data converted to list of rows (lists themselves)

    OUTPUT:

    pair of lists - low-lateral-dist intervals before button press, and low-lateral-dist intervals after button press.
    """

    dist = ldata[ps][4]

    bintervals = []
    binterval_length = 0
    binterval_distances = []
    aintervals = []
    ainterval_length = 0
    ainterval_distances = []

    for i in range(100):  # 50 is some max value, might replace later
        before_dist = ldata[ps-i][4]
        if ps-i < 1:  # need to avoid index out of range, although button press within first 5s is unlikely
            break

        if before_dist < 0.9*dist:  # require at least 20% dip in lateral distance
            binterval_length += 1
            binterval_distances.insert(0, before_dist)
        else:
            if binterval_length > 2:
                bintervals.append(
                    [ps-i, binterval_length, binterval_distances])
                binterval_length = 0
                binterval_distances = []

        # Don't look for oncoming cars if button press is over 10 rows long
        if pl >= 10:
            continue

        after_dist = ldata[ps+i][4]

        if after_dist < 0.9*dist:  # require at least 20% dip in lateral distance
            ainterval_length += 1
            ainterval_distances.append(after_dist)
        else:
            if ainterval_length > 1:
                aintervals.append(
                    [ps+i - ainterval_length, ainterval_length, ainterval_distances])
                ainterval_length = 0
                ainterval_distances = []

    return (bintervals, aintervals)


if __name__ == "__main__":

    csv_file = os.path.join(constants.DATA_HOME,
                            "20230112", "ANALOG31.TXT")
    csvr = read_csv(csv_file)
    ldata = make_ldata(csvr)

    press_starts, press_lengths = get_press_lengths_and_starts(ldata)
    press_starts, press_lengths = correct_press_lengths_and_starts(
        press_starts, press_lengths)
    press_timestamps = get_press_timestamps(ldata, press_starts)

    for i in range(len(press_starts)):
        bintervals, aintervals = find_passing_cars(
            press_starts[i], press_lengths[i], ldata)

        print("Event:", i)
        print("Press start:", press_starts[i])
        print("Before press intervals:", bintervals)
        print("After press intervals:", aintervals)
        print()
        i += 1

    # print("event_timestamps:", event_timestamps)
    # print("event lengths:", event_lengths)
    # print("min distances:", min_distances)
    # print("classifications:", classifications)

    """
    zipped = zip(event_timestamps, event_starts,
                 event_lengths)
    for entry in zipped:
        print(entry)
    """
