import json

import pandas as pd
import requests

GEO_SHAPE = 'GeoShape'

FP_DATA_BUFFER_JSON = 'ov_data_buffer_full.json'
FP_OV_ROUTE_SECTIONS_JSON = 'ov_route_sections.json'
DF_JSON_FUER_MAURUS = 'ov_route_sections_df.json'


def get_year_data_from_server(year):
    r = requests.get(
        f'https://daten.sg.ch//api/records/1.0/search/?dataset=frequenzen-offentlicher-verkehr&q=&rows=500&facet=fp_jahr&'
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


def buffer_data(df):
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
        buffer_data(df_data_per_stop)
    return df_data_per_stop


def initialize_df_ov_route_sections():
    columns = ['didok_nr_start',
               'didok_nr_ende',
               'linie',
               'richtung',
               GEO_SHAPE,
               'vm',
               'tu',
               'region',
               'kt',
               'gemeinde',
               'fp_jahr',
               'zeitraum',
               'besetzung',
               'zugestiegen',
               'kurse'
               'GeoPoint']
    df = pd.DataFrame(columns=columns)
    return df


def copy_if_available(df_src: pd.DataFrame, index, parameter_name_src, dict_destination, parameter_name_destination):
    if not df_src.at[index, parameter_name_src] == pd.np.nan:
        dict_destination[parameter_name_destination] = df_src.at[index, parameter_name_src]


def get_geopos(sequence_df, current_sequence):
    start_coordinates = sequence_df.at[current_sequence, 'geopos']

    end_coordinates = sequence_df.at[current_sequence + 1, 'geopos']
    if start_coordinates is None or end_coordinates is None:
        return None
    else:
        return {'type': 'LineString',
                'coordinates':
                    [start_coordinates[::-1],
                     end_coordinates[::-1]]}


def get_base_info(current_sequence):
    base_info = dict()
    copy_if_available(df_ov_stops, current_sequence, 'didok_nr', base_info, 'didok_nr_start'),
    copy_if_available(df_ov_stops, current_sequence + 1, 'didok_nr', base_info, 'didok_nr_ende'),
    copy_if_available(df_ov_stops, current_sequence, 'linie', base_info, 'linie'),
    copy_if_available(df_ov_stops, current_sequence, 'richtung', base_info, 'richtung'),

    base_info[GEO_SHAPE] = get_geopos(sequence_df, current_sequence)
    copy_if_available(df_ov_stops, current_sequence, 'region', base_info, 'region'),
    copy_if_available(df_ov_stops, current_sequence, 'kt', base_info, 'kt'),
    copy_if_available(df_ov_stops, current_sequence, 'gemeinde', base_info, 'gemeinde'),
    copy_if_available(df_ov_stops, current_sequence, 'vm', base_info, 'vm'),
    copy_if_available(df_ov_stops, current_sequence, 'tu', base_info, 'tu'),
    copy_if_available(df_ov_stops, current_sequence, 'fp_jahr', base_info, 'fp_jahr'),
    return base_info


def get_mofr_info(current_sequence):
    mofr_info = {'zeitraum': 'Mo - Fr'}
    copy_if_available(df_ov_stops, current_sequence, 'bes_mofr', mofr_info, 'besetzung'),
    copy_if_available(df_ov_stops, current_sequence, 'ein_mofr', mofr_info, 'zugestiegen'),
    copy_if_available(df_ov_stops, current_sequence, 'kurse_mofr', mofr_info, 'kurse'),
    mofr_info.update(base_info)
    return mofr_info


def get_sa_info(current_sequence):
    sa_info = {'zeitraum': 'Sa'}
    copy_if_available(df_ov_stops, current_sequence, 'bes_sa', sa_info, 'besetzung'),
    copy_if_available(df_ov_stops, current_sequence, 'ein_sa', sa_info, 'zugestiegen'),
    copy_if_available(df_ov_stops, current_sequence, 'kurse_sa', sa_info, 'kurse'),
    sa_info.update(base_info)
    return sa_info


def get_so_info(current_sequence):
    so_info = {'zeitraum': 'So'}
    copy_if_available(df_ov_stops, current_sequence, 'bes_so', so_info, 'besetzung'),
    copy_if_available(df_ov_stops, current_sequence, 'ein_so', so_info, 'zugestiegen'),
    copy_if_available(df_ov_stops, current_sequence, 'kurse_so', so_info, 'kurse'),
    so_info.update(base_info)
    return so_info


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    df_ov_stops = get_df_ov_stops()
    df_ov_route_sections = initialize_df_ov_route_sections()
    for line_df in df_ov_stops.groupby('linie'):
        for line_direction_df in line_df[1].groupby('richtung'):
            sequence_df = line_direction_df[1].sort_values('sequenz').copy()
            sequence_df.reset_index(inplace=True)
            for current_sequence in range(len(sequence_df) - 1):
                base_info = get_base_info(current_sequence)

                mofr_info = get_mofr_info(current_sequence)
                if mofr_info[GEO_SHAPE]:
                    df_ov_route_sections = df_ov_route_sections.append(mofr_info, ignore_index=True)

                sa_info = get_sa_info(current_sequence)
                if sa_info[GEO_SHAPE]:
                    df_ov_route_sections = df_ov_route_sections.append(sa_info, ignore_index=True)

                so_info = get_so_info(current_sequence)
                if so_info[GEO_SHAPE]:
                    df_ov_route_sections = df_ov_route_sections.append(so_info, ignore_index=True)

        print(f"Linie: {line_df[1]['linie'].values[0]}")

    # todo: improve nan handling --> not in dataset if nan
    df_ov_route_sections = df_ov_route_sections.fillna(0)

    df_ov_route_sections.to_json(DF_JSON_FUER_MAURUS)
    fields = df_ov_route_sections.to_dict('index')
    allmost_done_dict = list({'fields': entry} for entry in fields.values())
    outfile = open(FP_OV_ROUTE_SECTIONS_JSON, "w")
    json.dump(allmost_done_dict, outfile)
