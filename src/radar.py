from garmin_fit_sdk import Decoder, Stream

import csv
import os
import pandas as pd
import matplotlib.pyplot as plt

from src import constants


def radar_decode():

    fit_file = os.path.join(constants.DATA_HOME,
                            "20240330", "20240330_Forerunner645.fit")
    stream = Stream.from_file(fit_file)
    decoder = Decoder(stream)
    messages, errors = decoder.read()

    records = messages['record_mesgs']

    return records


def radar_unload():
    """
        Process data from the Garmin Varia radar into a list of events.
    """

    records = radar_decode()
    all_events = []

    prev = 0
    curr = 0
    count = 0
    for i, record in enumerate(records):
        date = str(record['timestamp']).split(' ')[0]
        time = str(record['timestamp']).split(' ')[1]
        position_lat = 0.0
        position_long = 0.0
        heart_rate = 0
        distance = 0.0
        temperature = 0
        enhanced_speed = 0.0 # bike's speed, corrected for glitches
        enhanced_altitude = 0.0 # bike's altitude, corrected for glitches
        # 8 position list. 
        # each position tracks distance to one of the cars behind the bike (up to 8 cars possible)
        radar_ranges = [] 
        radar_speeds = []
        radar_current = 0 # counter of overtakes/cars behind up to now
        passing_speed = 0 # speed of the car behind relative to bike's speed
        passing_speed_abs = 0 # absolute speed of the car behind
        if 'position_lat' in record:
            position_lat = record['position_lat']
        if 'position_long' in record:
            position_long = record['position_long']
        if 'heart_rate' in record:
            heartrate = record['heart_rate']
        if 'distance' in record:
            distance = record['distance']*1000 # to km
        if 'temperature' in record:
            distance = record['temperature']
        if 'enhanced_speed' in record:
            enhanced_speed = round(record['enhanced_speed']*3.6, 2)
        if 'enhanced_altitude' in record:
            enhanced_altitude = round(record['enhanced_altitude'], 2)
        if 'developer_fields' in record:
            radar_ranges = record.get('developer_fields').get(constants.RADAR_RANGES)[0] # assume always only 1 car behind
            radar_speeds = record.get('developer_fields').get(constants.RADAR_SPEEDS)[0]
            radar_current = record.get('developer_fields').get(constants.RADAR_CURRENT)
            passing_speed = record.get('developer_fields').get(constants.PASSING_SPEED), 
            passing_speed_abs = record.get('developer_fields').get(constants.PASSING_SPEED_ABS)

        # set passing_speed = 0 as the radar doesn't see a car once it's overtaking;
        my_record = [date, time, position_lat, position_long, heart_rate, distance, temperature, enhanced_speed, enhanced_altitude, radar_ranges, radar_speeds, radar_current, 0, passing_speed_abs]

        # -------------- if radar counter incremented ---------------
        my_event = [my_record]
        # then there must have been a car behind;
        # get the data;
        curr = record.get('developer_fields').get(constants.RADAR_CURRENT)
        if curr > prev:
            count += 1
            for j in range(1,40): # give car 40s to approach and overtakes
                car_dist_j =  records[i-j].get('developer_fields').get(constants.RADAR_RANGES)[0] 
                if car_dist_j > 0:
                    bike_speed = 0
                    if 'enhanced_speed' in records[i-j]:
                        bike_speed = round(records[i-j]['enhanced_speed']*3.6, 2)
                                        
                    my_record_j = [date, 
                                   str(records[i-j]['timestamp']).split(' ')[1],
                                   records[i-j]['position_lat'],
                                   records[i-j]['position_long'],
                                   records[i-j]['heart_rate'],
                                   records[i-j]['distance'],
                                   records[i-j]['temperature'],
                                   bike_speed,
                                   round(records[i-j]['enhanced_altitude'],2),
                                   records[i-j].get('developer_fields').get(constants.RADAR_RANGES)[0],
                                   records[i-j].get('developer_fields').get(constants.RADAR_SPEEDS)[0],
                                   records[i-j].get('developer_fields').get(constants.RADAR_CURRENT),
                                   records[i-j].get('developer_fields').get(constants.PASSING_SPEED),
                                   records[i-j].get('developer_fields').get(constants.PASSING_SPEED_ABS)]

                    my_event.append(my_record_j)
                else:
                    break
            radar_event_to_csv(os.path.join("out", "radar", str(record['timestamp'])+".csv"), my_event)

            prev += 1
        all_events.append(my_event)

    return all_events



def radar_event_to_csv(filename, event):

    header = ["date",
              "time",
              "position_lat",
              "position_long",
              "heart_rate",
              "distance",
              "temperature",
              "enhanced_speed", # the bicycle speed we want
              "enhanced_altitude",
              "car_distance",
              "car_speed_raw",
              "radar_count",
              "passing_speed_rel",
              "passing_speed_abs"]

    with open(filename, 'w') as f:
        csv_file = csv.writer(f)
        csv_file.writerow(header)
        csv_file.writerows(event)


def plot_radar_data():

    for filename in os.listdir(os.path.join("out", "radar")):
        if filename[-3:] != "csv":
            continue
        with open(os.path.join("out", "radar", filename),"r") as csv_file:
            df = pd.read_csv(csv_file)
            distances = df.car_distance
            rel_passing_speed = df.passing_speed_rel
            plt.plot(distances, rel_passing_speed)
            plt.xlim(3,100)
            plt.ylim(0,100)
            plt.savefig(os.path.join("out", "radar", filename[:-3]+".png"))
            plt.clf()


