#!/usr/bin/env python3

"""
Script to divide text into segmentable chunks (roughly corresponding to 
continuous text paragraphs)
"""


import sys
import re

import signal
signal.signal(signal.SIGPIPE, signal.SIG_DFL)	# avoid broken pipe exception


def tokenize_text(text):

	""" returns a list of tokens, i.e. either lines of text as
	they appear in `text` or paragraph/section delimiters """
	
	tokens = []	

	# split by paragraphs (>2 newline separators)
	paras = text.split('\n¶\n')

	# scan each paragraph
	for p in paras:
		
		ptokens = tokenize_paragraph(p)
		if ptokens:	# if paragraph not empty
			if tokens:	# if previous content exists
				tokens.append('¶')
			
			tokens += ptokens	# add content of this paragraph 

	return tokens


def tokenize_paragraph(ptext):

	""" returns a list of tokens from `ptext` """

	ptokens = []
			
	# split by sections (2 newline separators)
	secs = ptext.split('\n¤\n')

	# scan each section
	for s in secs:
	
		stokens = tokenize_section(s)
		if stokens:	# if section not empty
			if ptokens:	# if previous content exists
				ptokens.append('¤')
			
			ptokens += stokens	# add content of this section 
	
	return ptokens


def tokenize_section(stext):

	""" returns a list of tokens from `stext` """
	
	# split by single newlines
	lines = stext.split('\n')
	stokens = []
	for l in lines:
		l = l.strip()
		if l:	# if not empty line
			stokens.append(l)

	return stokens
	
	
	

# read input file as a single string
text = sys.stdin.read()

tokens = tokenize_text(text)	# return as a list of tokens

# scan tokens and group in chunks
chunks = []	# list of final chunks
chunk = []	# list of data for current chunk
ix = 0		# current token position
tokenl = len(tokens)
state = 'start'

while ix<tokenl:
	token = tokens[ix]
	ix += 1
	
	if state=='start':	# only when starting
		if token=='¶' or token=='¤': continue	# skip when starting
		# a text line token
		if token.startswith('@_SEC_@'):
			# add token without mark
			rtok = token[7:]
			if rtok:
				chunk.append(rtok)
				state = 'section'

		elif token.startswith('@_FIG_@'):
			state = 'caption'	# and skip

		else:
			# add line to current chunk
			chunk.append(token)
			#print('S',chunk)
			state = 'chunk'
	
	elif state=='chunk':	# while gathering a chunk	
		if token=='¶':
			state = 'chunk-maybe-cut'				
		elif token=='¤':
			pass	# ignore this if in 'chunk' state
		else:	# a text  line token
			if token.startswith('@_SEC_@'):
				# start a new chunk (even if mark has no text)
				if chunk:
					chunks.append(' '.join(chunk))
					chunk = []
				# add token without mark
				rtok = token[7:]
				if rtok:
					chunk.append(rtok)
					state = 'section'
					continue

			elif token.startswith('@_FIG_@'):
				pass	# TBD
			else:
				# add line to current chunk
				chunk.append(token)
				#print('C',chunk)
	
	elif state=='chunk-maybe-cut':
		# token here is a text line one
		if token.startswith('@_SEC_@'):
			# start a new chunk (even if mark has no text)
			if chunk:
				chunks.append(' '.join(chunk))
				chunk = []
			# add token without mark
			rtok = token[7:]
			if rtok:
				chunk.append(rtok)
				state = 'section'
				continue
			
		elif token.startswith('@_FIG_@'):
			pass	# TBD
		else:
			if token[0].isupper():
				# start a new chunk
				if chunk:
					chunks.append(' '.join(chunk))
					chunk = []
			chunk.append(token)
			#print('M',chunk)
		
		state='chunk'
			
	elif state=='section':			
		if token=='¶':
			# section done, start a new chunk
			chunks.append(' '.join(chunk))	# NOTE: chunk has always content here
			chunk = []
			state = 'chunk'
		
		elif token=='¤':
			pass	# ignore this
		
		else:	# text line token
			if token.startswith('@_SEC_@'):
				# section done, start a new section
				chunks.append(' '.join(chunk))	# NOTE: chunk has always content here
				chunk = []

				# add token without mark
				rtok = token[7:]
				if rtok:
					chunk.append(rtok)
					# state remains 'section'
				else:
					state = 'chunk'	# empty section text?
									
			elif token.startswith('@_FIG_@'):
				pass	# TBD
				
			else:	# accumulate in section text
				chunk.append(token)
			
			
	elif state=='caption':			
		if token=='¶' or token=='¤':
			# caption hopefully done
			state = 'chunk'
		
		
		else:	# text line token
			if token.startswith('@_SEC_@'):
				# caption done, start a new section
				if chunk:
					chunks.append(' '.join(chunk))
					chunk = []

				# add token without mark
				rtok = token[7:]
				if rtok:
					chunk.append(rtok)
					state = 'section'
				else:
					state = 'chunk'	# empty section text?
									
			elif token.startswith('@_FIG_@'):
				pass	# carry on skipping..
				
			else:	# accumulate in section text
				pass	# carry on skipping..
			

final = []	# the final assembled chunks list
for chunk in chunks:
	chunk = chunk.strip()
	if not final:
		final.append(chunk)
	else:
		# check for possible merges
		if chunk[0].islower() and final[-1][-1] not in ('.',':',';','?'):
			final[-1] = ' '.join((final[-1],chunk))
		else:
			final.append(chunk)		

# assemble output text
text = '\n'.join(final)

# output new text
sys.stdout.write(text)	



