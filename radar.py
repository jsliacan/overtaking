from garmin_fit_sdk import Decoder, Stream


import os
import constants


def main():

    fit_file = os.path.join(constants.DATA_HOME,
                            "20230112", "20230112_Forerunner645.fit")
    stream = Stream.from_file(fit_file)
    decoder = Decoder(stream)
    messages, errors = decoder.read()

    # for message in messages:
    records = messages['record_mesgs']
    prev = 0
    curr = 0
    count = 0
    for record in records:
        curr = record.get('developer_fields').get(constants.RADAR_CURRENT)
        if curr > prev:
            count += 1
            # print timestamp when radar_current was incremented
            print(count, record['timestamp'])
            prev += 1


if __name__ == "__main__":
    main()
