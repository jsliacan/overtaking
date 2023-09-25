import os
import csv
import constants, util
import matplotlib.pyplot as plt

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

    line = csv_file.readline()
    csv_reader = csv.reader(csv_file, delimiter="\t")
    if "," in line:
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

    # there *should be* a timestamp within every 22 rows, but sometimes that's 23 rows :/
    # example: 20221227, there are 22 rows strictly between timestamps at 382927 and 382950
    # make range 25 rows long
    for j in range(25):
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

        # only look for overtaking events if press length is > 7
        if pl > 7 and i < gap_to_prev:

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

        # don't look for oncoming events if press length is > 10
        if pl < 10 and i < gap_to_next:
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


def make_events(press_starts, press_lengths, ldata, date_string):
    """
    Event = [classification, flag, press_length, date_string, timestamp, event_start, dipped lat.dist. interval]

    classification  -- 1 for overtaking, -1 for oncoming
    flag            -- further information about how we arrived at the classification
                        0: press length > 10 or < 7, so we're confident it's overtaking and oncoming respectively
                        1: single event around the button press, so fairly sure that's it (cross-check with press length for overtake or oncoming)
                        2: many events to one side of the button press -- one-sided messy situation
                        3: took closest event, both sides of button press have distinct events -- double-sided situation
                        4: shared event between two button presses [error!]
    """

    flag_confident = 0
    flag_one_sided_single = 1
    flag_one_sided_messy = 2
    flag_double_sided = 3
    flag_shared = 4

    events = list()  # will hold overtaking/oncoming events

    for i in range(len(press_starts)):

        # initialize fields in the "event"
        classification = 0
        flag = -1
        press_length = press_lengths[i]
        event_timestamp = ""
        interval_info = []

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
            classification = 1
            flag = flag_confident

        elif press_lengths[i] <= 7:
            if len(aintervals) == 0:
                raise IndexError(
                    "No oncoming intervals found for this button press of length",
                    press_lengths[i],
                )
            interval_info = aintervals[0]
            event_timestamp = get_next_closest_timestamp(ldata, interval_info[0])
            classification = -1
            flag = flag_confident

        elif len(bintervals) == 0:  # oncoming
            interval_info = aintervals[0]
            event_timestamp = get_next_closest_timestamp(ldata, interval_info[0])
            classification = -1

            flag = flag_one_sided_single
            # if many "events" around the press, mark as one-sided messy
            if len(aintervals) > 2:
                flag = flag_one_sided_messy

        elif len(aintervals) == 0:  # overtaking
            interval_info = bintervals[0]
            event_timestamp = get_next_closest_timestamp(ldata, interval_info[0])
            classification = 1

            flag = flag_one_sided_single
            # if many "events" around the press, mark as one-sided messy
            if len(bintervals) > 2:
                flag = flag_one_sided_messy

        # both binervals and aintervals exist
        elif press_starts[i] - bintervals[0][0] < aintervals[0][0] - press_starts[i]:
            # closest binterval is closer to button press than closest ainterval
            # assume that's what the button press was about
            interval_info = bintervals[0]
            event_timestamp = get_next_closest_timestamp(ldata, interval_info[0])
            flag = flag_double_sided
            classification = 1

        else:
            # closest ainterval is closer to button press than closest binterval
            # assume that's what the button press was about
            interval_info = aintervals[0]
            event_timestamp = get_next_closest_timestamp(ldata, interval_info[0])
            flag = flag_double_sided
            classification = -1

        events.append([classification] + [flag] + [press_length] + [date_string] + [event_timestamp] + interval_info)
        # correct flag if necessary
        if i > 1 and len(events) > 1 and events[-1][4] == events[-2][4]:
            events[-1][1] = flag_shared
            events[-2][1] = flag_shared

    return events


if __name__ == "__main__":

    dflist = util.get_box_files(constants.DATA_HOME)
    util.ensure_date_in_filenames(dflist)  # renames files that don't contain date in filename
    dflist = util.get_box_files(constants.DATA_HOME)  # compile a list of filenames again after renaming

    for csv_file in dflist:
        csvr = read_csv(csv_file)
        ldata = make_ldata(csvr)  # CSV data as a list

        press_starts, press_lengths = get_press_lengths_and_starts(ldata)
        date_string = csv_file.split("/")[-1][:8]

        events = make_events(press_starts, press_lengths, ldata, date_string)
        for e in events:
            print(e)

    """
    box_files = util.get_box_files(constants.DATA_HOME)

    all_press_lengths = []

    for csv_file in box_files:
        print(csv_file)
        csvr = read_csv(csv_file)
        ldata = make_ldata(csvr)

        # press lenghts/starts are already corrected for interrupts
        press_starts, press_lengths = get_press_lengths_and_starts(ldata)
        all_press_lengths += press_lengths

    plt.hist(all_press_lengths, bins=50)
    plt.show()
    """
