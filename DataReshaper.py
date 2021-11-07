import json

import pandas as pd
import requests

START_YEAR = 2016
END_YEAR = 2021
APPENDIX = 'FULL'

GEO_SHAPE = 'GeoShape'

BASE_FOLDER = f'C:/Users/SimonKogler/OneDrive - originate GmbH/originate/Interne Projekte/OpenDataHack/data/'
FP_DATA_BUFFER_JSON = f'ov_data_buffer_{APPENDIX}.json'
FP_OV_ROUTE_SECTIONS_JSON = f'{BASE_FOLDER}ov_route_sections_{APPENDIX}.json'
DF_JSON_FOR_TRAFFIC_COUNTER = f'{BASE_FOLDER}ov_route_sections_{APPENDIX}_df.json'
BASE_REQUEST = f'https://daten.sg.ch//api/records/1.0/search/?dataset=frequenzen-offentlicher-verkehr&q=&rows=-1' \
               f'&facet=fp_jahr&facet=didok_nr&facet=haltestelle_didok&facet=bemerkung_tu' \
               f'&facet=linie&facet=vm&facet=sequenz'


def _get_year_data_from_server(_year):
    r = requests.get(
        f'{BASE_REQUEST}&refine.fp_jahr={_year}')
    if r:
        year_data = r.json()
        year_records = year_data['records']
        year_fields = list(record['fields'] for record in year_records)
        print(f'Datensatz {_year} empfangen')
        return pd.DataFrame(year_fields)


def _get_data_from_server():
    total_df = pd.DataFrame()
    for _year in range(START_YEAR, END_YEAR):
        if total_df.empty:
            total_df = _get_year_data_from_server(_year)
        else:
            total_df = total_df.append(_get_year_data_from_server(_year), ignore_index=True)
    return total_df


def _buffer_data(df):
    buffer_file = open(FP_DATA_BUFFER_JSON, "w")
    buffer_file.write(df.to_json())


def get_buffered_df(path=FP_DATA_BUFFER_JSON):
    try:
        return pd.io.json.read_json(path)
    except:
        return pd.DataFrame()


def get_df_ov_stops() -> pd.DataFrame:
    df_data_per_stop = get_buffered_df()
    if df_data_per_stop.empty:
        df_data_per_stop = _get_data_from_server()
        _buffer_data(df_data_per_stop)
        print(f'Datensatz unter {FP_DATA_BUFFER_JSON} für zukünftige offline Nutzung zwischengespeichert')
    return df_data_per_stop


def _initialize_df_ov_route_sections():
    columns = ['didok_nr_start',
               'didok_nr_ende',
               'haltestelle_didok_start',
               'haltestelle_didok_ende',
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


def _copy_if_available(df_src: pd.DataFrame, index, parameter_name_src, dict_destination, parameter_name_destination):
    if not df_src.at[index, parameter_name_src] == pd.np.nan:
        dict_destination[parameter_name_destination] = df_src.at[index, parameter_name_src]


def _fetch_geo_shape(sequence_df, _current_sequence):
    start_coordinates = sequence_df.at[_current_sequence, 'geopos']

    end_coordinates = sequence_df.at[_current_sequence + 1, 'geopos']
    try:
        return {'type': 'LineString',
                'coordinates':
                    [start_coordinates[::-1],
                     end_coordinates[::-1]]}
    except:
        return None


def get_base_info(df_src, _current_sequence):
    _base_info = dict()
    _copy_if_available(df_src, _current_sequence, 'didok_nr', _base_info, 'didok_nr_start'),
    _copy_if_available(df_src, _current_sequence + 1, 'didok_nr', _base_info, 'didok_nr_ende'),
    _copy_if_available(df_src, _current_sequence, 'haltestelle_didok', _base_info, 'haltestelle_didok_start'),
    _copy_if_available(df_src, _current_sequence + 1, 'haltestelle_didok', _base_info, 'haltestelle_didok_ende'),
    _copy_if_available(df_src, _current_sequence, 'linie', _base_info, 'linie'),
    _copy_if_available(df_src, _current_sequence, 'richtung', _base_info, 'richtung'),
    geo_shape = _fetch_geo_shape(df_sequence, _current_sequence)
    _base_info[GEO_SHAPE] = geo_shape
    if not geo_shape:
        print(f"Der folgende Streckenabschnitt wird verworfen, weil GeoInfos fehlen: {_base_info}")
    _copy_if_available(df_src, _current_sequence, 'region', _base_info, 'region'),
    _copy_if_available(df_src, _current_sequence, 'kt', _base_info, 'kt'),
    _copy_if_available(df_src, _current_sequence, 'gemeinde', _base_info, 'gemeinde'),
    _copy_if_available(df_src, _current_sequence, 'vm', _base_info, 'vm'),
    _copy_if_available(df_src, _current_sequence, 'tu', _base_info, 'tu'),
    _copy_if_available(df_src, _current_sequence, 'fp_jahr', _base_info, 'fp_jahr'),
    return _base_info


def get_mofr_info(df_src, _current_sequence, _base_info):
    _mofr_info = {'zeitraum': 'Mo - Fr'}
    _copy_if_available(df_src, _current_sequence, 'bes_mofr', _mofr_info, 'besetzung'),
    _copy_if_available(df_src, _current_sequence, 'ein_mofr', _mofr_info, 'zugestiegen'),
    _copy_if_available(df_src, _current_sequence, 'kurse_mofr', _mofr_info, 'kurse'),
    _mofr_info.update(_base_info)
    return _mofr_info


def get_sa_info(df_src, _current_sequence, _base_info):
    _sa_info = {'zeitraum': 'Sa'}
    _copy_if_available(df_src, _current_sequence, 'bes_sa', _sa_info, 'besetzung'),
    _copy_if_available(df_src, _current_sequence, 'ein_sa', _sa_info, 'zugestiegen'),
    _copy_if_available(df_src, _current_sequence, 'kurse_sa', _sa_info, 'kurse'),
    _sa_info.update(_base_info)
    return _sa_info


def get_so_info(df_src, _current_sequence, _base_info):
    _so_info = {'zeitraum': 'So'}
    _copy_if_available(df_src, _current_sequence, 'bes_so', _so_info, 'besetzung'),
    _copy_if_available(df_src, _current_sequence, 'ein_so', _so_info, 'zugestiegen'),
    _copy_if_available(df_src, _current_sequence, 'kurse_so', _so_info, 'kurse'),
    _so_info.update(_base_info)
    return _so_info


def write_out_results(_df_ov_route_sections):

    # todo: to be replaced with database request from TrafficCounter
    # TrafficCounter.py works with Pandas too, just export the whole df as json
    _df_ov_route_sections.to_json(DF_JSON_FOR_TRAFFIC_COUNTER)

    # todo: completely to be automated as link between the ov_stops database and the ov_route_sections database
    # get shape that open data tool presumably requires
    fields = _df_ov_route_sections.to_dict('index')
    allmost_done_dict = list({'fields': entry} for entry in fields.values())
    file_dataset_for_upload = open(FP_OV_ROUTE_SECTIONS_JSON, "w")
    json.dump(allmost_done_dict, file_dataset_for_upload)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    df_ov_stops = get_df_ov_stops()
    df_ov_route_sections = _initialize_df_ov_route_sections()
    year = 0

    # todo: performance presumably could be significantly optimized by using more appropriate pandas methods
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
                print(f"{df_sequence.at[0, 'fp_jahr']}: Linie {df_sequence.at[0, 'linie']} Richtung "
                      f"{df_sequence.at[0, 'richtung']} hinzugefügt")

    # todo: improve nan handling -->  zeros for all NaN could be wrong
    df_ov_route_sections = df_ov_route_sections.fillna(0)

    write_out_results(df_ov_route_sections)
