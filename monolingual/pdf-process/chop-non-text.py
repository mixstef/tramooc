#!/usr/bin/env python3

"""
Pipe script thar skips lines containing non-text (various methods of detection)
"""

import sys
import re
import unicodedata

import signal
signal.signal(signal.SIGPIPE, signal.SIG_DFL)	# avoid broken pipe exception


def is_text(line,count=1,minch=3):

	""" detects if a line contains 'textual' words
	(i.e. words with all letter characters).
	Each word to qualify mus have at least `minch` len.
	Count of these words must be equal or more than `count`
	to return True. Returns False otherwise """
	
	found = 0
	state = 'start'
	
	for uc in line:

		# find unicode category of char
		categ = unicodedata.category(uc)
		if categ.startswith('L'):	# a letter
			if state=='start' or state=='spacer':
				state = 'word'
				# candidate word start
				chlen = 1	# init word length
				
			elif state=='word':
				chlen += 1	# increment word length, remain to word state
		
			else:	# other chars, state was 'other'
				pass	# remain to 'other', don't count this as word

		elif categ.startswith('Z') \
		   or categ.startswith('C') \
		     or categ.startswith('P'):	# space, tab, newline, punctuation...
			if state=='word':	# word just ended
				# fast check if we are done
				if chlen>=minch: # qualifies as word!
					if found==count-1:
						return True
					# else, just increment found words
					found += 1
			# in any case, jump to spacer state
			state = 'spacer'
							     		
		else:	# not a letter
			# just go to 'other' state
			state = 'other'
	
	
	return False

# rexp for blank chars
rexp = re.compile('^[ \n\t¶¤]+$')


def is_blank(line):

	""" returns True if line is blank or contains artificial separator chars """
	
	if rexp.search(line):
		return True
	return False


def has_greek(text,minch=1):

	# returns True if text contains at least `minch` greek chars 

	count = 0
	for c in text:
		if c>='\u0386' and c<='\u03ce':
			count += 1
			if count>=minch: return True
	return False


# rexp to detect toc lines
toc_rexp = re.compile(r'([.] ?){3,}[^0-9]*[0-9ivxIVX]+(-[0-9]+)?\s*$')

def is_toc(line):

	""" returns True if line belongs to a TOC """
	
	if toc_rexp.search(line):
		return True
		
	return False
	

# set of unique lines
uset = set()

# rexp to find numericals with - or .
num_rexp = re.compile('[-.0-9ivx]+')

# rexp for figure or image caption numbering detection
figno_rexp = re.compile(r'^\s*(Εικ([όο]να)?|Σχ([ήη]μα|[έε]διο|εδι[άα]γραμμα|ήµα|νΐ|ήβΜ)?)\s*[-0-9.Γ]+(\s*:)?')
figno_rexp2 = re.compile(r'^\s*Σχήμα\s*[ΙIVXLSOHMΜlaßoóΑʹYU).0-9]+')
figno_rexp3 = re.compile(r'^\s*Σχήμα\s*:')

# rexp for section numbering detection
secno_rexp = re.compile(r'^\s*[-0-9ΑΒΓΔΕΖΗΘΙΚΛIVX.]+[.)](?=\s)')
secno_rexp2 = re.compile(r'^\s*([1-9][.])+[1-9](?=\s)')


for line in sys.stdin:
	
	if is_blank(line):	# pass blank lines as-is
		sys.stdout.write(line)
		
	elif is_text(line,3) and has_greek(line):	# lines with textual words with some greek chars
		
		if is_toc(line): continue	# skip lines belonging to tocs		
				
		if line in uset: continue	# skip already output line (e.g. repeating pdf headers)
		if num_rexp.sub('@_NUM_@',line) in uset: continue	# skip also with template
		
		uset.add(line)
		templ = num_rexp.sub('@_NUM_@',line)
		if templ!=line: uset.add(templ)	# add also template to set

		# replace any figure or image caption numberings
		line = figno_rexp.sub('@_FIG_@',line)
		line = figno_rexp2.sub('@_FIG_@',line)
		line = figno_rexp3.sub('@_FIG_@',line)
		
		# replace any section numberings
		line = secno_rexp.sub('@_SEC_@',line)
		line = secno_rexp2.sub('@_SEC_@',line)
		
		# skip all uppercased lines
		if line.isupper(): continue
				
		sys.stdout.write(line)
