from garmin_fit_sdk import Decoder, Stream

import csv
import os
import pandas as pd
import matplotlib.pyplot as plt

from src import constants, util

def fit_file_messages(filename):
    """
        Get all messages from FIT file ('message' is most high-level section, e.g. Record, Session, etc.) 

        filename: absolute path to a FIT file
    """

    stream = Stream.from_file(filename)
    decoder = Decoder(stream)
    messages, errors = decoder.read()

    return messages

def fit_get_session(messages):
    """
        Get the session message from FIT file messages. 

        messages: output of 'fit_file_messages'
    """

    session = messages['session_mesgs']

    return session
