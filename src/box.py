"""
Python3 script for analyzing data files from the device measuring
lateral-distance during overtaking.
"""
import csv
import matplotlib.pyplot as plt

import src.constants as constants
import src.util as util

ldata = []  # will hold contents of the CSV file in list format
all_events = [] # will hold all events from the data

def read_events_from_csvfile(filename):
    """
    Read in events that were already produced and saved to the 'data' folder, e.g. 'data/events.csv'.
    Parse them back to list of lists, with everything in or list of ints, except timestamp (stays string).
    """
    my_events = []
    with open(filename, encoding="utf-8") as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',')
        next(csv_reader) # skips header line
        for line in csv_reader:
            for i in [0,1,2,3,5,6]:
                line[i] = int(line[i])
            ldl = line[-1] # lat. dist. list
            ldl = ldl[1:-1].split(", ")
            line[-1] = []
            if ldl != [""]:
                ldl = [int(d) for d in ldl]
                line[-1] = ldl
            my_events.append(line)

    return(my_events)

def get_first_minimum(seq):
    """
    Returns the first minimum int it encounters in the list seq.
    """

    fmin = seq[0]
    for t in seq:
        if t < fmin:
            fmin = t
        elif t > fmin * 1.2:  # needs a robustness coeff so it doesn't end at a little fluctuation
            return fmin
    return fmin

def make_ldata(csv_reader):
    """
    Given a CSV reader, extract data from the CSV file.
    """

    ldat = list(csv_reader)

    # If this is a new file with Date field as the leftmost field (13 fields)
    # Delete the entire first column to match the earlier files
    if len(ldat[0]) == 13:
        print("Discarding the first column: 'Date' to align with earlier file structure.", flush=True)
        for i in range(len(ldat)):
            for j in range(1, len(ldat[i])):
                ldat[i][j-1] = ldat[i][j]
            ldat[i] = ldat[i][:-1]

        
    for i in range(len(ldat)):
        stripped4 = ldat[i][4].strip()
        stripped5 = ldat[i][5].strip()
        ldat[i][4] = int(stripped4)
        ldat[i][5] = int(stripped5)

    return ldat


def correct_press_lengths_and_starts(press_starts, press_lengths):
    """
    1. Check if any presses are only <2 rows apart. If yes,
    concatenate those presses. It is physically near-impossible to
    press button 2x (on purpose) only 1/11s apart.

    2. Check if two *short* presses or two *long* presses are only 4-5
    lines apart. If yes, discard the first press in such a pair. This
    was a "double-press" to indicate a long vehicle. We won't be doing
    double-presses in the future.

    3. Discard presses of length=1. Physically impossible to do on purpose.
    """

    for i in range(len(press_lengths)):
        print(press_starts[i], press_lengths[i])
    # Check for case 1.
    original_num_presses = len(press_starts)
    num_presses = original_num_presses
    offset = 2  # offset=1 is simply due to indexing from 0 to len-offset
    while True:
        for i in range(num_presses - offset):

            if i+1 < len(press_starts): # check if index in bounds

                if press_starts[i] + press_lengths[i] >= press_starts[i+1] - 2:
                    # keep press_start of the first press
                    # make its length sum of the two presses plus gap between them
                    press_lengths[i] = press_starts[i + 1] - press_starts[i] + press_lengths[i + 1]
                    press_lengths.pop(i + 1)  # remove the second press
                    press_starts.pop(i + 1)  # remove the second press
                    offset += 1

        if num_presses == original_num_presses:  # if no changes, done.
            break
        # if concatenated some presses, repeat.
        original_num_presses = num_presses

    # Check for case 2.
    i = 0
    while i < len(press_starts)-1:
        if press_starts[i] + press_lengths[i] >= press_starts[i+1] - 4:
            if press_lengths[i] < 10 and press_lengths[i+1] < 10:
                press_lengths.pop(i)
                press_starts.pop(i)
            elif press_lengths[i] > 10 and press_lengths[i+1] > 10:
                press_lengths.pop(i)
                press_starts.pop(i)
        i += 1

    # Check for case 3.
    i = 0
    while i < len(press_starts)-1:
        if press_lengths[i] == 1:
            press_lengths.pop(i)
            press_starts.pop(i)
        i += 1

    return (press_starts, press_lengths)


def get_press_lengths_and_starts(ldat):
    """
    Infer button presses from the data file and save start and
    length of each of them in two lists.
    """

    press_lengths = []
    press_starts = []
    len_press = 0

    i = 0
    for row in ldat:

        if row[5] == 1:
            if len_press == 0:
                press_starts.append(i)
            len_press += 1
            continue

        if (row[5] == 0 or i == len(ldat)) and len_press > 0:
            press_lengths.append(len_press)
            len_press = 0
        i += 1
    if len_press > 0:
        press_lengths.append(len_press)

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

    pair of lists - low-lateral-dist intervals before button press,
    and low-lateral-dist intervals after button press.
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

            if before_dist < 0.9 * dist:  # require at least 10% dip in lateral distance
                binterval_length += 1
                binterval_distances.insert(0, before_dist)
            else:
                if binterval_length > 0:
                    bintervals.append([ps - i, binterval_length, binterval_distances])
                    binterval_length = 0
                    binterval_distances = []

        if i < gap_to_next:
            after_dist = ldata[ps + i][4]

            if after_dist < 0.9 * dist:  # require at least 10% dip in lateral distance
                ainterval_length += 1
                ainterval_distances.append(after_dist)
            else:
                if ainterval_length > 0:
                    aintervals.append([ps + i - ainterval_length, ainterval_length, ainterval_distances])
                    ainterval_length = 0
                    ainterval_distances = []

    # POST-CORRECTION (bintervals only; overtakes)
    # If the event ends after the button press begins, then the above search won't find it.
    # If the event wasn't found (only length=1,2,3 lat.dist. dips found); then re-do search from end of button press.
    if len(bintervals) > 0 and max([len(interval[2]) for interval in bintervals]) < 3:
        dist = ldata[ps+pl][4]
        bintervals = []
        binterval_length = 0
        binterval_distances = []
        for i in range(100):
        # then most likely, the real interval started before button press ended.
        # re-run everything with button-press end, not start.
            before_dist = ldata[ps+pl - i][4]
            if ps+pl - i < 1:  # need to avoid index out of range, although button press within first 5s is unlikely
                break
            if before_dist < 0.9 * dist:  # require at least 10% dip in lateral distance
                binterval_length += 1
                binterval_distances.insert(0, before_dist)
            else:
                if binterval_length > 0:
                    bintervals.append([ps+pl - i, binterval_length, binterval_distances])
                    binterval_length = 0
                    binterval_distances = []

    return (bintervals, aintervals)

def pick_leftmost_interval_of_length(intervals, min_length):
    """
    Pick leftmost interval from the list of bintervals/aintervals
    whose length is at least min_length, or longest possible.
    """
  
    for interval in intervals:
        if len(interval[2]) > min_length:
            return interval
    # if no interval is longer than min_length return longest
    maxlen = 0
    candidate_interval = []
    for interval in intervals:
        if interval[1] > maxlen:
            maxlen = interval[1]
            candidate_interval = interval
    return candidate_interval

def make_events(press_starts, press_lengths, ldata, date_string):
    """
    Event = [classification, flag, press_length, date_string, timestamp, event_start, interval_length, interval]

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

    events = []  # will hold overtaking/oncoming events

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
            gap_to_prev = press_starts[i]
            gap_to_next = press_starts[i + 1] - press_starts[i]
        elif i == len(press_starts) - 1:
            gap_to_prev = press_starts[i] - press_starts[i - 1]
            gap_to_next = len(ldata) - press_starts[i]
        else:
            gap_to_prev = press_starts[i] - press_starts[i - 1]
            gap_to_next = press_starts[i + 1] - press_starts[i]

        bintervals, aintervals = find_events_for_press(press_starts[i], press_lengths[i], gap_to_prev, gap_to_next, ldata)

        # false event
        if len(bintervals) + len(aintervals) == 0:
            continue

        if press_lengths[i] >= 11:  # clear overtake
            interval_info = [press_starts[i], 0, []]
            if len(bintervals) == 0:
                # print("aintervals:", aintervals)
                # print("bintervals:", bintervals)
                print("No overtaking intervals found for the press starting at", press_starts[i], "with length", press_lengths[i])
            else:
                interval_info = pick_leftmost_interval_of_length(bintervals, 2)
            #interval_info = bintervals[0]
            event_timestamp = get_next_closest_timestamp(ldata, interval_info[0])
            classification = 1
            flag = flag_confident

        elif press_lengths[i] <= 9:
            interval_info = [press_starts[i], 0, []]
            if len(aintervals) == 0:
                # print("aintervals:", aintervals)
                # print("bintervals:", bintervals)
                print("No oncoming intervals found for the press starting at", press_starts[i], "with length", press_lengths[i])
            else:
                interval_info = aintervals[0]
            event_timestamp = get_next_closest_timestamp(ldata, interval_info[0])
            classification = -1
            flag = flag_confident

        elif len(bintervals) == 0:  # oncoming
            interval_info = aintervals[0]
            print(interval_info)
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


def collate_events():
    """
    Run make_events() on data from all available files and compile
    the events into one long list (global var all_events).
    """

    # initialize header
    header_str = "[classification, flag, press_length, date_string, timestamp, event_start, interval_length, interval]"

    all_events.append(header_str.strip("[]").split(", "))

    # get data
    dflist = util.get_box_files(constants.DATA_HOME)
    util.ensure_date_in_filenames(dflist)  # renames files that don't contain date in filename
    dflist = util.get_box_files(constants.DATA_HOME)  # compile a list of filenames again after renaming

    # process data
    print("collating data...", flush=True)
    for csv_file in dflist:
        print(csv_file, flush=True)
        csvr = util.read_csv(csv_file)
        ldata = make_ldata(csvr)  # CSV data as a list
        press_starts, press_lengths = get_press_lengths_and_starts(ldata)
        date_string = csv_file.split("/")[-1][:8]

        events = make_events(press_starts, press_lengths, ldata, date_string)
        all_events.extend(events)

    print("done.")
    return all_events
