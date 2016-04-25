#!/usr/bin/env python3

"""
Pipe script thar normalizes multiple spaces and newlines
"""

import sys
import re

import signal
signal.signal(signal.SIGPIPE, signal.SIG_DFL)	# avoid broken pipe exception

# space normalizing re
rexp1 = re.compile('[ \t]+')

# 2 consequtive \n collapsing re
rexp2 = re.compile('\n{2,}')

# >2 consequtive \n collapsing re
rexp2a = re.compile('\n{3,}')

# space+\n collapsing re
rexp3 = re.compile(' ?\n ?') 


# read input file as a single string
text = sys.stdin.read()

# normalize spaces
text = rexp1.sub(' ',text)

# collapse spaces around newline chars
text = rexp3.sub('\n',text)

# collapse multiple (>2) consecutive newlines to section sign
text = rexp2a.sub('\n¶\n',text)

# collapse 2 consecutive newlines to section sign
text = rexp2.sub('\n¤\n',text)

# output new text
sys.stdout.write(text)	

	 
