#!/usr/bin/env python3

import json
import os

# get file Path
filePath = os.path.abspath(os.getcwd())

# print (os.getcwd())
  
# Opening JSON file
f = open(filePath+'/segment-display/data.json')
data = json.load(f)

print(data)
  
# Closing file
f.close()