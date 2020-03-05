"""
Author: Alan Chen
NetId: ycchen4
"""

import pandas as pd
import numpy as np
from datetime import datetime
from geographiclib.geodesic import Geodesic
import math


def analyze_aircraft_data(file_name: str, update_interval=1):
    if file_name is "" or file_name is None:
        raise ValueError("file does not exist")

    with open(file_name, 'r') as input_file:
        start_time = None
        end_time = None
        time_gap = None
        data_in_interval = []
        colnames = ['TIME', '# Craft', 'Fastest (kts)', 'Highest (ft)', 'Msgs/Sec']
        result_df = pd.DataFrame(columns=colnames)

        # read line by line
        for line in input_file:
            current_line_list = line.split(',')

            # set up variables for interval calculation
            current_time = current_line_list[8] + ' ' + current_line_list[9]
            current_time = get_datetime_from_string(current_time)
            end_time = current_time
            if start_time is None:
                start_time = current_time
                print(start_time)

            cur_data_list = [current_line_list[i] for i in [8, 9, 4, 11, 12, 14, 15]]
            data_in_interval.append(cur_data_list)

            time_interval = (end_time - start_time).total_seconds()
            if time_interval >= update_interval * 60:
                print(end_time)
                print("------ data_in_interval ------")
                # TODO: Output CURRENT and CUMULATIVE result

                time_col = end_time.strftime("%m/%d %H:%M:%S")
                print('time_col = ', time_col)
                # start_time = None
                # end_time = None

                # init the pandas data frame
                col_names = ['DateLogged', 'TimeLogged', 'AircraftHex', 'Altitude', 'GroundSpeed', 'Latitude', 'Longitude']
                data_frame = pd.DataFrame(data=data_in_interval, columns=col_names)

                # craft & Fastest
                craft_no_col = len(data_frame.groupby('AircraftHex').agg(['count']))
                print('craft_no_col = ', craft_no_col)

                # fastest
                fastest_col = get_max_by('GroundSpeed', data_frame.groupby(['AircraftHex'])['GroundSpeed'].max().reset_index())
                print('fastest_col = ', fastest_col)

                # Highest
                highest_col = get_max_by('Altitude', data_frame.groupby(['AircraftHex'])['Altitude'].max().reset_index())
                print('highest_col = ', highest_col)

                # Msgs / Sec
                msg_per_sec_col = round(data_frame.shape[0] / time_interval, 1)
                print('data_frame.shape[0] = ', data_frame.shape[0])
                print('time_interval = ', time_interval)
                print(msg_per_sec_col)


                result_df.loc[0] = [time_col, craft_no_col, fastest_col, highest_col, msg_per_sec_col]

                print(result_df)

                break


def get_max_by(type: str, df: pd.DataFrame) -> str:
    max_speed = df[type].max()
    max_speed_craft = df[df[type] == max_speed]

    return str(max_speed_craft.iloc[0]['AircraftHex']) + ' ' + str(max_speed_craft.iloc[0][type])


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


def calculate_the_distance(last_latitude: float, last_longitude: float, current_latitude: float, current_longitude: float) -> float:
    if is_valid(last_latitude) and is_valid(last_longitude) and is_valid(current_latitude) and is_valid(current_longitude):
        geod = Geodesic.WGS84
        distance = round(
        geod.Inverse(last_latitude, last_longitude, current_latitude, current_longitude)['s12'] / 1852.0, 2)

    return 0.0


def is_valid(f: float):
    if math.isnan(f) or f is not None:
        return True


if __name__ == '__main__':
    analyze_aircraft_data('data/Jan15_3_hours.csv')
