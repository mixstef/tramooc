#!/usr/bin/env python3

import sys,os
import re

# rexp to find segmentation points
rexp = re.compile(r'(^| )(\w+)([.])(?=($| [A-Z0-9a-z\u0386-\u03ce\[]))')

# rexp to find starting line bullets
rexp2 = re.compile('^[-*]\s*')

def has_greek(text):

	for c in text:
		if c>='\u0386' and c<='\u03ce':
			return True
	return False

with open(sys.argv[1],'r') as ifp:

		
	path,ext = os.path.splitext(sys.argv[1])
	ofname = path+'.txt-presegmented'


	
	with open(ofname,'w') as ofp:
	
		# read input file as a single string
		text = ifp.read()

		# replace paragraph signs with \n
		text = text.replace('\n§\n','\n')

		# split on newlines
		presegments = text.split('\n')

		# remember visited lines
		visited = set()

		# process each presegment
		for preseg in presegments:
	
			# replace internal segmentation points with \n
			preseg = rexp.sub('\\1\\2\\3\n',preseg)
			l = preseg.split('\n')
			for internal in l:
				if internal in visited: continue
			
				visited.add(internal)
				if has_greek(internal):	# check if line contains greek chars
					internal = internal.strip()	# remove any leading or trailing ws
					# eliminate starting bullets, if any
					internal = rexp2.sub('',internal)
					ofp.write(internal.strip()+'\n')	
