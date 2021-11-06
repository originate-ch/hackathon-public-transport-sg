import json

import pandas as pd
import requests

START_YEAR = 2016
END_YEAR = 2021
APPENDIX = 'VBSG'

GEO_SHAPE = 'GeoShape'

FP_DATA_BUFFER_JSON = f'ov_data_buffer_{APPENDIX}.json'
FP_OV_ROUTE_SECTIONS_JSON = f'ov_route_sections_{APPENDIX}.json'
DF_JSON_FUER_MAURUS = f'ov_route_sections_{APPENDIX}_df.json'


def get_year_data_from_server(year):
    r = requests.get(
        f'https://daten.sg.ch//api/records/1.0/search/?dataset=frequenzen-offentlicher-verkehr&q=&rows=-1&facet=fp_jahr&'
        f'facet=didok_nr&facet=haltestelle_didok&facet=bemerkung_tu&facet=linie&facet=vm&facet=sequenz&refine.fp_jahr={year}&refine.tu=VBSG')
    if r:
        year_data = r.json()
        year_records = year_data['records']
        year_fields = list(record['fields'] for record in year_records)
        return pd.DataFrame(year_fields)


def get_data_from_server():
    total_df = pd.DataFrame()
    for year in range(START_YEAR, END_YEAR):
        if total_df.empty:
            total_df = get_year_data_from_server(year)
        else:
            total_df = total_df.append(get_year_data_from_server(year), ignore_index=True)
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
               'kurse']
    df = pd.DataFrame(columns=columns)
    return df


def copy_if_available(df_src: pd.DataFrame, index, parameter_name_src, dict_destination, parameter_name_destination):
    if not df_src.at[index, parameter_name_src] == pd.np.nan:
        dict_destination[parameter_name_destination] = df_src.at[index, parameter_name_src]


def get_geopos(sequence_df, _current_sequence):
    start_coordinates = sequence_df.at[_current_sequence, 'geopos']

    end_coordinates = sequence_df.at[_current_sequence + 1, 'geopos']
    if start_coordinates is None or end_coordinates is None:
        return None
    else:
        return {'type': 'LineString',
                'coordinates':
                    [start_coordinates[::-1],
                     end_coordinates[::-1]]}


def get_base_info(df_src, _current_sequence):
    _base_info = dict()
    copy_if_available(df_src, _current_sequence, 'didok_nr', _base_info, 'didok_nr_start'),
    copy_if_available(df_src, _current_sequence + 1, 'didok_nr', _base_info, 'didok_nr_ende'),
    copy_if_available(df_src, _current_sequence, 'linie', _base_info, 'linie'),
    copy_if_available(df_src, _current_sequence, 'richtung', _base_info, 'richtung'),

    _base_info[GEO_SHAPE] = get_geopos(df_sequence, _current_sequence)
    copy_if_available(df_src, _current_sequence, 'region', _base_info, 'region'),
    copy_if_available(df_src, _current_sequence, 'kt', _base_info, 'kt'),
    copy_if_available(df_src, _current_sequence, 'gemeinde', _base_info, 'gemeinde'),
    copy_if_available(df_src, _current_sequence, 'vm', _base_info, 'vm'),
    copy_if_available(df_src, _current_sequence, 'tu', _base_info, 'tu'),
    copy_if_available(df_src, _current_sequence, 'fp_jahr', _base_info, 'fp_jahr'),
    return _base_info


def get_mofr_info(df_src, _current_sequence, _base_info):
    _mofr_info = {'zeitraum': 'Mo - Fr'}
    copy_if_available(df_src, _current_sequence, 'bes_mofr', _mofr_info, 'besetzung'),
    copy_if_available(df_src, _current_sequence, 'ein_mofr', _mofr_info, 'zugestiegen'),
    copy_if_available(df_src, _current_sequence, 'kurse_mofr', _mofr_info, 'kurse'),
    _mofr_info.update(_base_info)
    return _mofr_info


def get_sa_info(df_src, _current_sequence, _base_info):
    _sa_info = {'zeitraum': 'Sa'}
    copy_if_available(df_src, _current_sequence, 'bes_sa', _sa_info, 'besetzung'),
    copy_if_available(df_src, _current_sequence, 'ein_sa', _sa_info, 'zugestiegen'),
    copy_if_available(df_src, _current_sequence, 'kurse_sa', _sa_info, 'kurse'),
    _sa_info.update(_base_info)
    return _sa_info


def get_so_info(df_src, _current_sequence, _base_info):
    _so_info = {'zeitraum': 'So'}
    copy_if_available(df_src, _current_sequence, 'bes_so', _so_info, 'besetzung'),
    copy_if_available(df_src, _current_sequence, 'ein_so', _so_info, 'zugestiegen'),
    copy_if_available(df_src, _current_sequence, 'kurse_so', _so_info, 'kurse'),
    _so_info.update(_base_info)
    return _so_info


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    df_ov_stops = get_df_ov_stops()
    df_ov_route_sections = initialize_df_ov_route_sections()
    year = 0
    for df_year in df_ov_stops.groupby('fp_jahr'):
        for df_line in df_year[1].groupby('linie'):
            for df_line_direction in df_line[1].groupby('richtung'):
                df_sequence = df_line_direction[1].sort_values('sequenz').copy()
                df_sequence.reset_index(inplace=True)
                for current_sequence in range(len(df_sequence) - 1):
                    base_info = get_base_info(df_sequence, current_sequence)

                    mofr_info = get_mofr_info(df_sequence, current_sequence, base_info)
                    if mofr_info[GEO_SHAPE]:
                        df_ov_route_sections = df_ov_route_sections.append(mofr_info, ignore_index=True)

                    sa_info = get_sa_info(df_sequence, current_sequence, base_info)
                    if sa_info[GEO_SHAPE]:
                        df_ov_route_sections = df_ov_route_sections.append(sa_info, ignore_index=True)

                    so_info = get_so_info(df_sequence, current_sequence, base_info)
                    if so_info[GEO_SHAPE]:
                       df_ov_route_sections = df_ov_route_sections.append(so_info, ignore_index=True)
                print(df_sequence.at[0, 'linie'])

    # todo: improve nan handling --> not in dataset if nan
    df_ov_route_sections = df_ov_route_sections.fillna(0)

    df_ov_route_sections.to_json(DF_JSON_FUER_MAURUS)
    fields = df_ov_route_sections.to_dict('index')
    allmost_done_dict = list({'fields': entry} for entry in fields.values())
    outfile = open(FP_OV_ROUTE_SECTIONS_JSON, "w")
    json.dump(allmost_done_dict, outfile)
