#!/usr/bin/python3

import sys
import struct


filename = sys.argv[1]
buffer_size = 4096*1024*11
le = False
fieldtype = "h"
fieldsize = 2   

if le:
    bo = '<'
else:
    bo = '>'


with open(filename,'rb') as file:
    chunk = file.read(buffer_size)
    bytearr = list(struct.unpack(bo+fieldtype*int(buffer_size/fieldsize), chunk))
    #while chunk:
    #    bytearr.append(list(struct.unpack(bo+fieldtype*int(buffer_size/fieldsize), chunk)))

print("read")





searches = [
[0,0,0,0,1,2,0,4,3,2,7,6,8,6,9,6,10,7,11,13],
[0,0,0,0,2,3,3,3,2,3,5,1,3,2,3,2,0,5,5],

[0,0,0,0,0,0,0,6,5,3,3,6,4,1,11,11,6,8,6,8],
[0,0,0,0,2,4,3,1,5,11,3,5,7,5,5,5,7,10,9,13,12],
[0,0,0,0,2,2,4,4,1,2,4,4,3,4,9,4,8,5,15,12,9],
[0,0,0,0,3,4,2,1,5,1,3,7,4,7,4,6,8,10,10,22,23],
[0,0,0,0,0,0,0,6,5,3,3,6,4,1,11,11,6,8,6,8,5],
[0,0,0,0,1,3,2,4,8,6,4,4,4,6,5,6,11,10,8,12],
]
last = 0
search = searches.pop(0)
window_size = len(search)
print(f"Searching for {search}")
for i in range(len(bytearr) - window_size +1):
    test =   bytearr[i: i + window_size]
    if test[0] == search[0]:
        if test == search:
            print(f"Found @{i}, {i-last} from last")
            last = i
            search = searches.pop(0)
            window_size = len(search)
            print(f"Searching for {search}")
            
