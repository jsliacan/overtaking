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
        elif t > fmin * 1.2:  # needs a robustness coeff so it doesn't end at a little fluctuation
            return fmin
    return fmin


def read_csv(filename):
    """Read CSV file and return a reader."""
    csv_file = open(filename, newline="")
    csv_reader = csv.reader(csv_file, delimiter=",")

    return csv_reader


def make_ldata(csv_reader):

    ldata = list(csv_reader)
    for i in range(1, len(ldata)):
        ldata[i][4] = int(ldata[i][4].strip())
        ldata[i][5] = int(ldata[i][5].strip())

    return ldata


def correct_press_lengths_and_starts(press_starts, press_lengths):
    """
    Check if any presses are only <2 rows apart. If yes, concatenate those presses.

    It is physically near-impossible to press button 2x (on purpose) only 1/11s apart.
    """

    original_num_presses = len(press_starts)
    num_presses = original_num_presses
    offset = 2  # offset=1 is simply due to indexing from 0 to len-offset

    while True:
        for i in range(num_presses - offset):

            # if button presses are too close to each other
            if press_starts[i] + press_lengths[i] >= press_starts[i + 1] - 2:
                # keep press_start of the first press
                # make its length sum of the two presses plus gap between them
                press_lengths[i] = press_starts[i + 1] - press_starts[i] + press_lengths[i + 1]
                press_lengths.pop(i + 1)  # remove the second press
                press_starts.pop(i + 1)  # remove the second press
                offset += 1

        if num_presses == original_num_presses:  # if no changes, done.
            break
        else:
            # if concatenated some presses, repeat.
            original_num_presses = num_presses

    return (press_starts, press_lengths)


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

    return correct_press_lengths_and_starts(press_starts, press_lengths)


def get_next_closest_timestamp(ldata, line_number):
    """
    Works for getting the closest timestamp forward in time for a button press
    or an event that begins on `line_number` in `ldata`.
    """

    timestamp = ""

    for j in range(22):  # there's a timestamp within every 22 rows
        timestamp = ldata[line_number + j][0].strip()
        if timestamp != "":
            break

    return timestamp


def find_events_for_press(ps, pl, gap_to_prev, gap_to_next, ldata):
    """Returns a lit of before-intervals and after-intervals for each button press.

    INPUT:

    ps          -- row where the button press starts in ldata
    pl          -- length of the button press starting at row ps
    gap_to_next -- number of rows to the closest next button press_start
    gap_to_prev -- number of rows to the closest previous button press_start
    ldata       -- csv data converted to list of rows (lists themselves)

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

    for i in range(100):  # 100 is some max value (~4s), might replace later

        if i < gap_to_prev:

            before_dist = ldata[ps - i][4]
            if ps - i < 1:  # need to avoid index out of range, although button press within first 5s is unlikely
                break

            if before_dist < 0.9 * dist:  # require at least 20% dip in lateral distance
                binterval_length += 1
                binterval_distances.insert(0, before_dist)
            else:
                if binterval_length > 0:
                    bintervals.append([ps - i, binterval_length, binterval_distances])
                    binterval_length = 0
                    binterval_distances = []

        # Don't look for oncoming cars if button press is over 10 rows long
        if pl >= 10:
            continue

        if i < gap_to_next:
            after_dist = ldata[ps + i][4]

            if after_dist < 0.9 * dist:  # require at least 20% dip in lateral distance
                ainterval_length += 1
                ainterval_distances.append(after_dist)
            else:
                if ainterval_length > 0:
                    aintervals.append([ps + i - ainterval_length, ainterval_length, ainterval_distances])
                    ainterval_length = 0
                    ainterval_distances = []

    return (bintervals, aintervals)


def make_events(press_starts, press_lengths, ldata):
    """
    Event = [flag, timestamp, press_start, dipped lat.dist. interval]

    Flags:

        0 -- press length > 10, so quite sure it's overtaking
        1 -- only 1 event around the button press, so fairly sure that's it (whether overtake or oncoming)
        2 -- took closest event, both sides of button press have a distinct event
        3 -- many events around button press -- messy situation
        4 -- shared event between two button presses [error!]
    """

    flag0 = 0
    flag1 = 1
    flag2 = 2
    flag3 = 3
    flag4 = 4

    events = list()  # will hold overtaking/oncoming events

    for i in range(len(press_starts)):

        gap_to_next = 0
        gap_to_prev = 0
        if i == 0:
            gap_to_next = press_starts[i + 1] - press_starts[i]
        elif i == len(press_starts) - 1:
            gap_to_prev = press_starts[i] - press_starts[i - 1]
        else:
            gap_to_prev = press_starts[i] - press_starts[i - 1]
            gap_to_next = press_starts[i + 1] - press_starts[i]

        bintervals, aintervals = find_events_for_press(press_starts[i], press_lengths[i], gap_to_prev, gap_to_next, ldata)

        # false event
        if len(bintervals) + len(aintervals) == 0:
            continue

        if press_lengths[i] >= 10:  # clear overtake
            if len(bintervals) == 0:
                raise IndexError(
                    "No overtaking intervals found for this button press of length",
                    press_lengths[i],
                )
            interval_info = bintervals[0]
            event_timestamp = get_next_closest_timestamp(ldata, interval_info[0])
            events.append([flag0] + [event_timestamp] + interval_info)

        elif len(bintervals) == 0:  # oncoming
            interval_info = aintervals[0]
            event_timestamp = get_next_closest_timestamp(ldata, interval_info[0])
            events.append([flag1] + [event_timestamp] + interval_info)

        elif len(aintervals) == 0:  # overtaking
            interval_info = bintervals[0]
            event_timestamp = get_next_closest_timestamp(ldata, interval_info[0])
            events.append([flag1] + [event_timestamp] + interval_info)

        elif press_starts[i] - bintervals[0][0] < aintervals[0][0] - press_starts[i]:  # both binervals and aintervals exist!
            # closest binterval is closer to button press than closest ainterval
            # assume that's what the button press was about
            interval_info = bintervals[0]
            event_timestamp = get_next_closest_timestamp(ldata, interval_info[0])
            flag = 2
            if len(bintervals) + len(aintervals) > 2:
                flag = 3
            events.append([flag] + [event_timestamp] + interval_info)

        else:
            # closest ainterval is closer to button press than closest binterval
            # assume that's what the button press was about
            interval_info = aintervals[0]
            event_timestamp = get_next_closest_timestamp(ldata, interval_info[0])
            flag = 2
            if len(bintervals) + len(aintervals) > 2:
                flag = 3
            events.append([flag] + [event_timestamp] + interval_info)

        # correct flag if necessary
        if i > 1 and events[-1][2] == events[-2][2]:
            events[-1][0] = 4  # mark them as shared events (by 2 different button presses)
            events[-2][0] = 4

    return events


if __name__ == "__main__":

    csv_file = os.path.join(constants.DATA_HOME, "20230112", "ANALOG31.TXT")
    csvr = read_csv(csv_file)
    ldata = make_ldata(csvr)  # CSV data as a list

    press_starts, press_lengths = get_press_lengths_and_starts(ldata)

    events = make_events(press_starts, press_lengths, ldata)
    for e in events:
        print(e)

    """
    for i in range(len(press_starts)):
        bintervals, aintervals = find_passing_cars(
            press_starts[i], press_lengths[i], ldata)

        print("Event:", i)
        print("Press start:", press_starts[i])
        print("Before press intervals:", bintervals)
        print("After press intervals:", aintervals)
        print()
        i += 1
    """
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
