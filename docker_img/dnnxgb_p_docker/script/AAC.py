#!/usr/bin/env python
#_*_coding:utf-8_*_

import re
from collections import Counter

def AAC(sequence, **kw):
	AA ='ACDEFGHIKLMNPQRSTVWY'
	encodings = []
	header = ['#']
	for i in AA:
		header.append(i)
	encodings.append(header)
	code = []
	count = Counter(sequence)
	for key in count:
			count[key] = count[key]/len(sequence)

	for aa in AA:
			code.append(count[aa])
	return code

