import json
import random

records = list()
for i in range(5):
    fields = dict()
    fields['bes_sa'] = random.uniform(1, 2)
    fields['bes_so'] = random.uniform(1, 2)
    fields['vm'] = 'Bus'
    fields['bes_jahr'] = random.uniform(1, 2)
    fields['linie'] = '432'
    fields['richtung'] = 'Sargans'
    fields['tu'] = 'BOS'
    fields['bes_mofr'] = random.uniform(1, 2)
    fields['didok_nr_start'] = '8574822'
    fields['didok_nr_stop'] = '8574822'
    fields['gemeinde'] = 'Mels'
    fields['fp_jahr'] = '2020'
    fields['aus_mofr'] = random.uniform(1, 2)
    fields['kurse_mofr'] = random.uniform(1, 2)
    fields['kurse_so'] = random.uniform(1, 2)
    fields['region'] = 'Sarganserland-Werdenberg'
    fields['kurse_sa'] = random.uniform(1, 2)
    fields['kt'] = 'SG'
    fields['GeoShape'] = {
                             "type": "LineString",
                             "coordinates": [[random.uniform(9.39, 9.395), random.uniform(47.43, 47.434)],
                                             [random.uniform(9.39, 9.395), random.uniform(47.43, 47.434)],
                                             [random.uniform(9.39, 9.395), random.uniform(47.43, 47.434)]]
                         },
    fields['zugestiegen_mofr'] = random.uniform(1, 2)
    fields['zugestiegen_sa'] = random.uniform(1, 2)
    fields['zugestiegen_so'] = random.uniform(1, 2)

    record = dict()
    record['fields'] = fields

    records.append(record)

a = json.dumps(records)
print(a)
