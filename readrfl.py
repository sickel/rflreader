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
'filehead': "<cccc"+"H"*61, # Signature, version? unknown, unknown, samplelength, unknown.
'samplehead': "<BBBLHH", # Unkonwn, unkonwn, samplecounter, UTC, systemconstant
'unithead': "<"+"bbLH", # Unknown, Unknown, UTC-time +1 sec, number of chs.
'spectrehead': "<"+"H"*5+"B"*2+"H"*8+"I"+"H"*14+"I"+"H"*4, # 14B unknown,2BCrystalid, 2B sample#  pr detector (rollover after 255), I livetime (us/s) ,29: Total count
'spectre': False, # To be determined from unithead
'spectretail': "<"+"H"*(269), # 0 - 255: Downsampled spectre
'unittail': "<bbbbLHH"+"H"*74,    
'sampletail':  "<"+"H"*3+"bbddd"+"H"*61, # Unknown, smplflag?,unknown, unknown, smplflag? , ECEF X, ECEF Y, ECEF Z, unknowns
}

print('spectre#,blocktype,start')
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
    datasize = int(datasize/10)


prevsample = None
ignoreerror = False

measurements = []
sample = {'units':[]}
while start <= datasize:
    # Five crystals in one detectors
    # Four detectors in one sample
    try:
        if (i)%20 == 0: 
            st = 'samplehead'
            (sampledata,start,readfrom) = readchunk(structs[st],start,data)
            sampleid = sampledata[2]
            if not ignoreerror and prevsample is not None:
                if (prevsample + 1) % 256 != sampleid:
                    sys.exit(4)
            print(f"{i+1},{st},{readfrom},{sampledata}")
            sample = {'units':[], 'epoch': sampledata[3],'sampleid':sampleid}
            prevsample = sampleid
        if (i)%5 == 0: 
            st = 'unithead'
            unit = {'spectres':[]}
            (unitdata,start,readfrom) = readchunk(structs[st],start,data)
            print(f"{i+1},{st},{readfrom},{unitdata}")
            unit['epochnext'] = unitdata[2]
            if not structs ['spectre']:
                structs['spectre'] = "<"+"H"*unitdata[3]
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
            sample['sample#']=sampletaildata[6]
            measurements.append(sample)
            
        i += 1
    except struct.error as e:
        if not samplefinished:
            # Read incomplete data sets
            print(f"Reading error in {st}")
            print(e)
            sys.exit(5)
        break
if os.environ.get("RFL_DUMPDATA"):
    print(measurements, file = sys.stderr)
