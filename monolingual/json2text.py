#!/usr/bin/env python3

import sys,os
import json

print(sys.argv[1])
with open(sys.argv[1],'r') as ifp:
	jso = json.load(ifp)
		
	path,ext = os.path.splitext(sys.argv[1])
	ofname = path+'.txt'
	
	with open(ofname,'w') as ofp:
		ofp.write(jso[0]['X-TIKA:content'])
	

