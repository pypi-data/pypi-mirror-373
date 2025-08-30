#!/usr/bin/env python3

#---------------------------------
# Author: Ankit Anand
# Date: 12/08/25
# Email: ankit0.anand0@gmail.com
#---------------------------------

from pathlib import Path

def load_ann(path):
	"""
	Load annotation from audatity label text file.

	Parameters
	----------
	path: str
		label text file path.

	Returns
	-------
	list[tuple, ...]
		- annotation data structure
		- [(start, end, tag), ...]
	"""
	
	if not isinstance(path, (str, Path)):
		raise ValueError(f"`path` must be one of (str, Path), got {type(path)}")
	
	ann = []
	with open(str(path), "r") as f:
		lines = [line.rstrip("\n") for line in f]
		for line in lines:
			start, end, tag = line.split("\t")
			start, end = float(start), float(end)
			ann.append((start, end, tag))
			
	return ann