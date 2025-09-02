


'''
	
'''

import pathlib
from os.path import dirname, join, normpath
import sys
import os

def seek_recursively_towards_core ():
	return;


def seek_essence (packet):
	the_name = packet ["name"]

	env_vars = os.environ.copy ()
	if ("essence_path" in env_vars):
		return env_vars ["essence_path"]

	CWD = os.getcwd ()
	
	found_essence_path = False
	possible_directory = CWD	
	while True:
		possible_location = str (normpath (join (possible_directory, the_name)));
		print ("checking for essence:", possible_location)
		
		if os.path.exists (possible_location):
			found_essence_path = possible_location
			print ("essence found @:", possible_location)
			break;
			
		possible_directory = os.path.dirname (possible_directory)
			
		if (possible_directory == "/"):
			break;
			
			
	if (type (found_essence_path) != str):
		raise Exception (f"{ the_name } not found")
		
	return found_essence_path
			