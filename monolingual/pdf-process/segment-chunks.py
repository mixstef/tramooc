#!/usr/bin/env python3

"""
Script to segment chunks (paragraphs) of text
"""


import sys
import re

import signal
signal.signal(signal.SIGPIPE, signal.SIG_DFL)	# avoid broken pipe exception


def has_greek(text,minch=1):

	# returns True if text contains at least `minch` greek chars 

	count = 0
	for c in text:
		if c>='\u0386' and c<='\u03ce':
			count += 1
			if count>=minch: return True
	return False


# rexp for candidate segment points
cseg_rexp = re.compile(r'(^| )([^ ]+) ?([.!;])(?=($| [A-Z\u0386-\u038f\u0391-\u03ab\[\u2206\u2126]))') 

# debug only rexp
#deb_rexp = re.compile(r'\.(?!_¶_)')

# rexp to detect some bullets or other spurious chars together with trailing spaces
bul_rexp = re.compile(r'[•]\s*')

# function called when a match is found
def match_seg(m):
	prefix = m.group(1)
	text = m.group(2)
	separator = m.group(3)
	suffix = m.group(4)	# NOTE: this is captured, but NOT matched!
		
	return ''.join([prefix,text,separator,'_¶_'])


# read chunks (one per line) from input
for line in sys.stdin:
	line = line.strip()
	
	# replace some bullet chars
	line = bul_rexp.sub('',line)
		
	newline = cseg_rexp.sub(match_seg,line)
	
	# debug only
	#newline = deb_rexp.sub('\033[30;107m.\033[0m',newline)
	
	# split chunk to specified segments
	segments = newline.split('_¶_')

	# output segments, one per line
	for seg in segments:
		if seg!='' and has_greek(seg): sys.stdout.write('{}\n'.format(seg.strip()))

