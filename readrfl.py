#!/usr/bin/python3

import sys
import struct
import os

filename = sys.argv[1]
searchchar = False
if len(sys.argv[2]):
    searchchar = sys.argv[2]

blocklength = 53997
specblocklength = 2658
head = 216


with open(filename,'rb') as file:
    data = file.read()
    
print("read")
print(len(data))
if searchchar: # Used for searching for values in first block
    longlong = "<"+(searchchar*20)
    longlonglength = struct.calcsize(longlong)
    for i in range(struct.calcsize(searchchar)):
        start = i
        while start < blocklengths:
            print(i,start,struct.unpack_from(longlong,data,start))
            start += longlonglength
    sys.exit()

def readchunk(pattern,start,data):
    last = start
    returndata = struct.unpack_from(pattern,data,start)
    newstart = start + struct.calcsize(pattern)
    return returndata,newstart,start

#fileheadstruct = ">"+"H"*72
structs = {
#'spectrehead': "<"+"H"*36,
'spectrehead': "<"+"H"*14+"I"+"H"*20, # 28B unknown , I livetime (us/s) , 40B unknown
'spectre': "<"+"H"*1024,
'spectretail': "<"+"H"*(1329-1024-36),
'unitblock': "<"+"H"*84,
'unitend': "<b"+"H"*74,
'unitstart': "<"+"bbbLHHHLH", # Unknown, Unknown, UTC-time, Unknown, Unknown, Unknown, UTC-time +1 sec, number of chs.
'rectail': "<"+"H"*9+"bddd"+"H"*61, # Unknown x10, ECEF X, ECEF Y, ECEF Z, unknown
'filehead': "<cccc"+"H"*61 # Signature, version? unknown, unknown, blocklength, unknown...
}
spectresize = struct.calcsize(structs['spectre'])

(filehead,start,readfrom) = readchunk(structs['filehead'],0,data)
print(f"0,filehead,{readfrom},{filehead}")
print(filehead[7])
for i in range(201):
    if (i)%20 == 0 and i > 0:
        st = 'rectail'
        (recheaddata,start,readfrom) = readchunk(structs[st],start,data)
        print(f"{i+1},{st},{readfrom},{recheaddata}")
    if (i)%5 == 0: # and i > 0 :
        st = 'unitstart'
        (unitdata,start,readfrom) = readchunk(structs[st],start,data)
        print(f"{i+1},{st},{readfrom},{unitdata}")
    if (i > 0) or True:
        st ='spectrehead'
        (spectrehead,start,readfrom) = readchunk(structs[st],start,data)
        print(f"{i+1},{st},{readfrom},{spectrehead}")
    st = 'spectre'
    (spectre,start,readfrom) = readchunk(structs[st],start,data)
    print(f"{i+1},{st},{readfrom},{spectre}")
    st = 'spectretail'
    (spectretail,start,readfrom) = readchunk(structs[st],start,data)
    print(f"{i+1},{st},{readfrom},{spectretail}")
    if (i+1)%5 == 0:
        st = 'unitend'
        (unitend,start,readfrom) = readchunk(structs[st],start,data)
        print(f"{i+1},{st},{readfrom},{unitend}")
    
    #print(i+1,start,spectre[0:10],spectre[-60:])
