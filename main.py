from garmin_fit_sdk import Decoder, Stream
from constants import *

import os


def main():

    print(DATA_HOME)
    fit_file = os.path.join(DATA_HOME,
                            "20230112", "20230112_Forerunner645.fit")
    stream = Stream.from_file(fit_file)
    decoder = Decoder(stream)
    messages, errors = decoder.read()

    # for message in messages:
    last_entry = messages['record_mesgs'][-1]
    print(last_entry.keys())
    print(last_entry.get('developer_fields').get(RADAR_CURRENT))


if __name__ == "__main__":
    main()
