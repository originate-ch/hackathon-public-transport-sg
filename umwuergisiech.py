# This is a sample Python script.

# Press Umschalt+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import pandas as pd
import requests

FP_DATA_BUFFER_JSON = 'ov_data_buffer.json'


def get_year_data_from_server(year):
    r = requests.get(
        f'https://daten.sg.ch//api/records/1.0/search/?dataset=frequenzen-offentlicher-verkehr&q=&rows=-1&facet=fp_jahr&'
        f'facet=didok_nr&facet=haltestelle_didok&facet=bemerkung_tu&facet=linie&facet=vm&facet=sequenz&refine.fp_jahr={year}')
    if r:
        year_data = r.json()
        year_records = year_data['records']
        year_fields = list(record['fields'] for record in year_records)
        return pd.DataFrame(year_fields)


def get_data_from_server():
    total_df = pd.DataFrame()
    for year in range(2016, 2020):
        if total_df.empty:
            total_df = get_year_data_from_server(year)
        else:
            total_df.append(get_year_data_from_server(year))
    return total_df


def buffer_df(df):
    buffer_file = open(FP_DATA_BUFFER_JSON, "w")
    buffer_file.write(df.to_json())


def get_buffered_df():
    try:
        return pd.io.json.read_json(FP_DATA_BUFFER_JSON)
    except:
        return pd.DataFrame()


def get_df_ov_stops() -> pd.DataFrame:
    df_data_per_stop = get_buffered_df()
    if df_data_per_stop.empty:
        df_data_per_stop = get_data_from_server()
        buffer_df(df_data_per_stop)
    return df_data_per_stop


def initialize_df_ov_route_sections():
    columns = ['didok_nr_start',
               'didok_nr_ende',
               'linie',
               'richtung',
               'GeoShape',
               'vm',
               'tu',
               'fp_jahr',
               'zeitraum',
               'besetzung',
               'zuegestiegen',
               'kurse']
    df = pd.DataFrame(columns=columns)
    return df


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    df_ov_stops = get_df_ov_stops()
    df_ov_route_sections = initialize_df_ov_route_sections()
    for line_df in df_ov_stops.groupby('linie'):
        for line_direction_df in line_df[1].groupby('richtung'):
            sequence_df = line_direction_df[1].sort_values('sequenz').copy()
            sequence_df.reset_index(inplace=True)
            for i in range(len(sequence_df) - 1):
                base_info = {
                    'didok_nr_start': sequence_df.at[i, 'didok_nr'],
                    'didok_nr_ende': sequence_df.at[i + 1, 'didok_nr'],
                    'linie': sequence_df.at[i, 'linie'],
                    'richtung': sequence_df.at[i, 'richtung'],
                    'GeoShape': sequence_df.at[i, 'linie'],
                    'vm': sequence_df.at[i, 'vm'],
                    'tu': sequence_df.at[i, 'tu'],
                    'fp_jahr': sequence_df.at[i, 'fp_jahr']}
                mofr_info = {
                    'zeitraum': 'Mo - Fr',
                    'besetzung': sequence_df.at[i, 'bes_mofr'],
                    'zuegestiegen': sequence_df.at[i, 'ein_mofr'],
                    'kurse': sequence_df.at[i, 'kurse_mofr'],
                }
                mofr_info.update(base_info)
                df_ov_route_sections.append(mofr_info, ignore_index=True)
                sa_info = {
                    'zeitraum': 'Sa',
                    'besetzung': sequence_df.at[i, 'bes_sa'],
                    'zuegestiegen': sequence_df.at[i, 'ein_sa'],
                    'kurse': sequence_df.at[i, 'kurse_sa'],
                }
                sa_info.update(base_info)
                df_ov_route_sections.append(mofr_info, ignore_index=True)
                so_info = {
                    'zeitraum': 'So',
                    'besetzung': sequence_df.at[i, 'bes_so'],
                    'zuegestiegen': sequence_df.at[i, 'ein_so'],
                    'kurse': sequence_df.at[i, 'kurse_so'],
                }
                so_info.update(base_info)
                df_ov_route_sections.append(mofr_info, ignore_index=True)

            print('uii')
