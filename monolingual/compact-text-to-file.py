#!/usr/bin/env python3

import sys,os
import re

# space normalizing re
rexp1 = re.compile('[ \t]+')

# \n collapsing re
rexp2 = re.compile('\n{2,}')

# space+\n collapsing re
rexp3 = re.compile(' ?\n ?') 


#print(sys.argv[1])
with open(sys.argv[1],'r') as ifp:

		
	path,ext = os.path.splitext(sys.argv[1])
	ofname = path+'.txt-compacted'


	
	with open(ofname,'w') as ofp:
	
		# read input file as a single string
		text = ifp.read()
	
		# normalize spaces
		text = rexp1.sub(' ',text)
	
		# collapse spaces around newline chars
		text = rexp3.sub('\n',text)
	
		# collapse multiple consecutive newlines to paragraph sign
		text = rexp2.sub('\n§\n',text)
	
		ofp.write(text)	
