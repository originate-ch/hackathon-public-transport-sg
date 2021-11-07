import pandas as pd

import DataReshaper

APPENDIX = 'FULL'

PATH_OV_ROUTE_SECTIONS_DF = f'{DataReshaper.BASE_FOLDER}ov_route_sections_{APPENDIX}_df.json'
TARGET_EXCEL_LOCATIONS = f'{DataReshaper.BASE_FOLDER}FlowmapFeederLocations.csv'
TARGET_EXCEL_FLOWS = f'{DataReshaper.BASE_FOLDER}FlowmapFeederFlows.csv'


def get_first_item(_list):
    if _list:
        return _list[0]


def get_second_item(_list):
    if _list:
        return _list[1]


df_ov_route_sections = DataReshaper.get_buffered_df(PATH_OV_ROUTE_SECTIONS_DF)
df_ov_stops = DataReshaper.get_df_ov_stops()

# choose subset
df_ov_route_sections = df_ov_route_sections[df_ov_route_sections.tu == 'VBSG']
df_ov_stops = df_ov_stops[df_ov_stops.tu == 'VBSG']

df_unique_stops = df_ov_stops.drop_duplicates(subset=['didok_nr'])
df_unique_stops = df_unique_stops.dropna(subset = ['didok_nr'])
df_locations = pd.DataFrame(columns=['id', 'name', 'lat', 'lon'])
df_locations['id'] = df_unique_stops['didok_nr'].astype(int)
df_locations['name'] = df_unique_stops['haltestelle_didok']
df_locations['lat'] = df_unique_stops['geopos'].apply(get_first_item)
df_locations['lon'] = df_unique_stops['geopos'].apply(get_second_item)
df_locations.to_csv(TARGET_EXCEL_LOCATIONS, index=False)


df_2019_mofr = df_ov_route_sections[df_ov_route_sections['fp_jahr'] == 2019]
df_2019_mofr = df_2019_mofr[df_2019_mofr['zeitraum'] == 'Mo - Fr']
df_flows = pd.DataFrame(columns=['origin', 'dest', 'count'])
df_flows['origin'] = df_2019_mofr['didok_nr_start']
df_flows['dest'] = df_2019_mofr['didok_nr_ende']
df_flows['count'] = df_2019_mofr['besetzung']
df_flows.to_csv(TARGET_EXCEL_FLOWS, index=False)
