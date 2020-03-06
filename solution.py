"""
Author: Alan Chen
NetId: ycchen4
"""

import pandas as pd
import math
from datetime import datetime
from geographiclib.geodesic import Geodesic


def analyze_aircraft_data(file_name: str, update_interval=5):
    """
    The main function to process the raw data line by line
    Output the data each update_interval
    :param file_name: The file name of raw aircraft data
    :param update_interval: The int value represent how many minutes the user want to output the analysis result
    :return: None
    """
    if file_name is "" or file_name is None:
        raise ValueError("file does not exist")

    with open(file_name, 'r') as input_file:
        start_time = None
        end_time = None
        data_in_interval = []
        current_result_col_names = ['TIME', '# Craft', 'Fastest (kts)', 'Highest (ft)', 'Msgs/Sec']
        cumulative_result_df = pd.DataFrame(columns=['#Craft', 'LongestTrack', '(nm)'])

        count = 0

        for line in input_file:
            current_line_list = line.split(',')

            # set up variables for interval calculation
            current_time = current_line_list[8] + ' ' + current_line_list[9]
            current_time = get_datetime_from_string(current_time)
            end_time = current_time
            if start_time is None:
                start_time = current_time

            cur_data_list = [current_line_list[i] for i in [8, 9, 4, 11, 12, 14, 15]]
            data_in_interval.append(cur_data_list)

            time_interval = (end_time - start_time).total_seconds()
            if time_interval >= update_interval * 60:
                """ CURRENT RESULTS """
                time_col = end_time.strftime("%m/%d %H:%M:%S")

                # -------- reset start and end time --------
                start_time = end_time
                end_time = None

                # -------- init the current result data frame --------
                col_names = ['DateLogged', 'TimeLogged', 'AircraftHex', 'Altitude', 'GroundSpeed', 'Latitude',
                             'Longitude']
                current_result_df = pd.DataFrame(data=data_in_interval, columns=col_names)

                # reset the data frame
                data_in_interval = []

                # -------- number of aircraft --------
                craft_no_col = len(current_result_df.groupby('AircraftHex').agg(['count']))

                # -------- fastest --------
                temp_df = current_result_df[['AircraftHex', 'GroundSpeed']]
                temp_df = temp_df[temp_df['GroundSpeed'] != '']
                fastest_col = get_max_value_by_type('GroundSpeed', temp_df)

                # -------- Highest --------
                temp_df = current_result_df[['AircraftHex', 'Altitude']]
                temp_df = temp_df[temp_df['Altitude'] != '']
                highest_col = get_max_value_by_type('Altitude', temp_df)

                # -------- Msgs / Sec --------
                msg_per_sec_col = round(current_result_df.shape[0] / time_interval, 1)

                new_df = pd.DataFrame(columns=current_result_col_names)
                new_df.loc[0] = [time_col, craft_no_col, fastest_col, highest_col, msg_per_sec_col]
                # current_result_df = pd.concat([current_result_df, new_df])

                if count == 0:
                    print("***************** CURRENT RESULTS ******************* | ******* CUMULATIVE RESULTS *******")
                    print('TIME # Craft  Fastest  (kts)  Highest  (ft)  Msgs/Sec')

                print(time_col, craft_no_col, fastest_col, highest_col, msg_per_sec_col)

                """CUMULATIVE RESULTS"""
                temp_df = current_result_df[['AircraftHex', 'Latitude', 'Longitude']]
                temp_df = temp_df[(temp_df['Latitude'] != '') & (temp_df['Longitude'] != '')]
                temp_df = temp_df.astype({'Latitude': 'float', 'Longitude': 'float'})
                distance_sum_df = temp_df.groupby(['AircraftHex']).apply(shift_sum).reset_index()
                distance_sum_df.columns = ['AircraftHex', 'Total_Distance']
                distance_sum_df = distance_sum_df.sort_values('Total_Distance', ascending=False)
                print(distance_sum_df)
                return

                # cumulative_result_df = pd.concat([cumulative_result_df, current_distance_df])
                # print(cumulative_result_df)


def shift_sum(df: pd.DataFrame) -> float:
    # if the data frame only has one row, remove it
    if df.shape[0] == 1:
        return 0.0

    # create two new columns(previous lat and lon) for distance calculation
    df[['prev_lat', 'prev_lon']] = df[['Latitude', 'Longitude']].shift(axis=0, periods=1)

    # calculate from the second row, and reset the index of df
    select_df = df[['prev_lat', 'prev_lon', 'Latitude', 'Longitude']].iloc[1:].reset_index(drop=True)

    # apply the calculate_the_distance() on each row
    distance_sum = sum(select_df.apply(calculate_the_distance, axis=1))

    return distance_sum


def calculate_the_distance(row: pd.Series) -> float:
    geod = Geodesic.WGS84
    total_distance = round(geod.Inverse(row[0], row[1], row[2], row[3])['s12'] / 1852.0, 6)
    return total_distance


def get_max_value_by_type(column_name: str, df: pd.DataFrame) -> str:
    """
    Get the maximum value of Altitude or Ground Speed
    :param column_name: string type, 'Altitude' or 'Groundspeed'
    :param df: the target data frame
    :return: the output string
    """
    df[column_name] = df[column_name].replace('', 0).astype(float)
    group_df = df.groupby(['AircraftHex'])[column_name].max().reset_index()
    group_df = group_df.sort_values(column_name, ascending=False)

    # get the max value from row 0, col all
    max_value = group_df.iloc[0, :]
    return str(max_value[0]) + ' ' + str(math.trunc(max_value[1]))


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
