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
print("x y z")
for sample in measurements:
    if sample['gpsxyz'] != (0,0,0):
        x,y,z=sample['gpsxyz']
        # print(x,y,z)
        lon1, lat1, alt1 = transformer.transform(x,y,z,radians=False)
        print (lat1, lon1, alt1 )
