#!/usr/bin/python3

import sys
import pyproj

transformer = pyproj.Transformer.from_crs(
    {"proj":'geocent', "ellps":'WGS84', "datum":'WGS84'},
    {"proj":'latlong', "ellps":'WGS84', "datum":'WGS84'},
    )
from rflreader import rflreader

filename = sys.argv[1]
reader = rflreader(filename)
readfrom,measurements = reader.rflparse()
print("lat lon alt epoch livetime specter altitude temperature pressure")
for sample in measurements:
    if sample['gpsxyz'] != (0,0,0):
        nadd = 0
        sample['temperature'] = None
        sample['pressure'] = None
        spectredata = []
        livetime = 0
        for unit in sample['units']:
            for idx,spectre in enumerate(unit['spectres']):
                if idx < 4 and spectre['livetime'] > 0:
                    nadd += 1
                    livetime += spectre['livetime']
                    if spectredata == []:
                        spectredata = spectre['spectre']
                    else:
                        spectredata = [x+y for x,y in zip(spectredata,spectre['spectre'])]
            for idx in ('temperature','pressure'):
                if not unit[idx] is None:
                    sample[idx] = unit[idx]
        livetime = livetime/nadd
        
        x,y,z=sample['gpsxyz']
        
        # print(x,y,z)
        lon1, lat1, alt1 = transformer.transform(x,y,z,radians=False)
        print (round(lat1,6), round(lon1,6), round(alt1,1), sample['epoch'], livetime, ','.join([str(x) for x in spectredata]), sample['altitude'], sample['temperature'], sample['pressure'] )
