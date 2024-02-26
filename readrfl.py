#!/usr/bin/python3

import sys
import struct
import os

filename = sys.argv[1]
searchchar = False
if len(sys.argv) >2:
    searchchar = sys.argv[2]
"""
Filestructur: Each sample is combined of 0 -4 detectors
each detector having 0 -5 crystals
one spectre is collected for each detector.

There is a file header, a header and footer for  each detector and each spectre
there is a footer for each sample
"""

samplelength= 53997
speclength= 2658
head = 216


with open(filename,'rb') as file:
    data = file.read()
    
datasize = len(data)

def readchunk(pattern,start,data):
    last = start
    returndata = struct.unpack_from(pattern,data,start)
    newstart = start + struct.calcsize(pattern)
    return returndata,newstart,start

structs = {
'spectrehead': "<"+"H"*14+"I"+"H"*20, # 28B unknown , I livetime (us/s) , 40B unknown
'spectre': False, # To be determined from unitstart
'spectretail': "<"+"H"*(1329-1024-36),
'unittail': "<b"+"H"*74,    
'unitstart': "<"+"bbbLHHHLH", # Unknown, Unknown, UTC-time, Unknown, Unknown, Unknown, UTC-time +1 sec, number of chs.
'sampletail': "<"+"H"*9+"bddd"+"H"*61, # Unknown x10, ECEF X, ECEF Y, ECEF Z, unknowns
'filehead': "<cccc"+"H"*61 # Signature, version? unknown, unknown, samplelength, unknown...
}

(filehead,start,readfrom) = readchunk(structs['filehead'],0,data)
print(f"0,filehead,{readfrom},{filehead}")
signature = b''.join(filehead[0:4])

#  Checking that the file is as expected

if signature != b'RSRL':
    print('Wrong file type signature: ',signature)
    sys.exit(2)

if filehead[4] != 1:
    print(f'Wrong file version: {filehead[4]}')
    sys.exit(3)
    

if filehead[7] != samplelength:
    print(f"Expected samplelength {samplelength}, found samplelength {filehead[7]}")
    sys.exit(3)

if searchchar: 
    # Used for searching for values in first block
    # Reading out all possible places for a given datatype within the first block
    longlong = "<"+(searchchar*20)
    longlonglength = struct.calcsize(longlong)
    for i in range(struct.calcsize(searchchar)):
        start = i
        while start < samplelength:
            print(i,start,struct.unpack_from(longlong,data,start))
            start += longlonglength
    sys.exit()
    
i = 0
if os.environ.get("RFL_READLIMIT") == '1':
    # To be used to have a smaller output for testing
    datasize = 500000
    
measurements = []
sample = {'units':[]}
while start <= datasize:
    try:
        if (i)%5 == 0: # and i > 0 :
            st = 'unitstart'
            unit = {'spectres':[]}
            (unitdata,start,readfrom) = readchunk(structs[st],start,data)
            # 'unitstart': "<"+"bbbLHHHLH", # Unknown, Unknown, UTC-time, Unknown, Unknown, Unknown, UTC-time +1 sec, number of chs.
            unit['epoch'] = unitdata[3]
            unit['epochnext'] = unitdata[7]
            print(f"{i+1},{st},{readfrom},{unitdata}")
            if not structs ['spectre']:
                structs['spectre'] = "<"+"H"*unitdata[8]
        st ='spectrehead'
        (spectrehead,start,readfrom) = readchunk(structs[st],start,data)
        print(f"{i+1},{st},{readfrom},{spectrehead}")
        spectredata={'livetime':spectrehead[14]}
        st = 'spectre'
        (spectre,start,readfrom) = readchunk(structs[st],start,data)
        spectredata['spectre'] = spectre
        unit['spectres'].append(spectredata)
        print(f"{i+1},{st},{readfrom},{spectre}")
        st = 'spectretail'
        (spectretail,start,readfrom) = readchunk(structs[st],start,data)
        print(f"{i+1},{st},{readfrom},{spectretail}")
        if (i+1)%5 == 0:
            st = 'unittail'
            (unitend,start,readfrom) = readchunk(structs[st],start,data)
            print(f"{i+1},{st},{readfrom},{unitend}")
            sample['units'].append(unit)
        samplefinished = False
        if (i+1)%20 == 0:
            st = 'sampletail'
            samplefinished = True
            (sampletaildata,start,readfrom) = readchunk(structs[st],start,data)
            print(f"{i+1},{st},{readfrom},{sampletaildata}")
            # 'sampletail': "<"+"H"*9+"bddd"+"H"*61, # Unknown x10, ECEF X, ECEF Y, ECEF Z, unknowns
            sample['gpsxyz']=sampletaildata[10:13]
            measurements.append(sample)
            sample = {'units':[]}
        i += 1
    except struct.error as e:
        if not samplefinished:
            # Read incomplete data sets
            print("Reading error")
            print(st)
            print(e)
            sys.exit(5)
        break
print(measurements, file = sys.stderr)
