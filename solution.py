"""
Author: Alan Chen
NetId: ycchen4
"""
from geographiclib.geodesic import Geodesic
import pandas as pd
from datetime import datetime

geod = Geodesic.WGS84


def analyze_aircraft_data(file_name: str, update_interval=1):
    if file_name is "" or file_name is None:
        raise ValueError("file does not exist")

    with open(file_name, 'r') as input_file:
        current_line_count = 0
        start_time = None
        end_time = None
        time_gap = None

        for line in input_file:
            current_line_list = line.split(',')

            current_time = current_line_list[8] + ' ' + current_line_list[9]
            current_time = get_datetime_from_string(current_time)
            if start_time is None:
                start_time = current_time
                print(start_time)

            end_time = current_time
            time_gap = end_time - start_time

            current_line_count += 1

            if time_gap.total_seconds() >= update_interval * 60:
                print(end_time)
                print('number of lines =', current_line_count)
                # TODO: Output CURRENT and CUMULATIVE result
                break




def get_datetime_from_string(date_string: str) -> datetime:
    """
    convert the input string into datetime object
    :param date_string: the string with specific format
    :return: datetime object gerated from input string
    >>> get_datetime_from_string("")
    Traceback (most recent call last):
    ValueError: string is empty

    >>> get_datetime_from_string(None)
    Traceback (most recent call last):
    ValueError: string is empty
    """
    if date_string is "" or date_string is None:
        raise ValueError("string is empty")

    date_format = "%Y/%m/%d %H:%M:%S.%f"
    datetime_obj = datetime.strptime(date_string, date_format)
    return datetime_obj



if __name__ == '__main__':
    analyze_aircraft_data('data/Jan15_3_hours.csv')
