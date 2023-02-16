

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


def get_event_lengths_and_starts(ldata):

    event_lengths = list()
    event_starts = list()
    len_event = 0

    i = 0
    for row in ldata:

        if row[5] == 1:
            if len_event == 0:
                event_starts.append(i)
            len_event += 1

        if row[5] == 0 and len_event > 0:
            event_lengths.append(len_event)
            len_event = 0

        i += 1

    return (event_lengths, event_starts)


def get_event_timestamps(ldata, event_starts):

    timestamps = []

    for es in event_starts:
        for j in range(22):  # there's a timestamp every 22nd row
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


def find_passing_car(event_starts, ldata):
    """
    Returns min overtaking or meeting distances and classification guess 
    between overtaking and oncoming.

    event_starts    -- indices of event starts in ldata
    ldata           -- csv data as a list


    Return:

        (list of(min dist), list of(-1/1)) 
    """

    min_distances = []
    classifications = []

    dist = 0
    for es in event_starts:

        dist = ldata[es][4]

        for i in range(50):  # 50 is some max value, might replace later
            before_dist = ldata[es-i][4]
            after_dist = ldata[es+i][4]

            if before_dist < 0.9*dist:  # require at least 20% dip in lateral distance
                dist_seq = [ldata[es-j][4] for j in range(100)]
                min_distances.append(get_first_minimum(dist_seq))
                classifications.append(1)  # it's overtaking
                break
            elif after_dist < 0.9*dist:  # require at least 20% dip in lateral distance
                dist_seq = [ldata[es+j][4] for j in range(100)]
                min_distances.append(get_first_minimum(dist_seq))
                classifications.append(-1)  # it's oncoming
                break

            if i == 49:
                min_distances.append(9999)
                classifications.append(0)

    return (min_distances, classifications)


if __name__ == "__main__":

    csv_file = os.path.join(constants.DATA_HOME,
                            "20230112", "ANALOG31.TXT")
    csvr = read_csv(csv_file)
    ldata = make_ldata(csvr)

    event_lengths, event_starts = get_event_lengths_and_starts(ldata)
    event_timestamps = get_event_timestamps(ldata, event_starts)
    min_distances, classifications = find_passing_car(event_starts, ldata)

    # print("event_timestamps:", event_timestamps)
    # print("event lengths:", event_lengths)
    # print("min distances:", min_distances)
    # print("classifications:", classifications)

    zipped = zip(event_timestamps, event_starts,
                 event_lengths, min_distances, classifications)

    for entry in zipped:
        print(entry)
