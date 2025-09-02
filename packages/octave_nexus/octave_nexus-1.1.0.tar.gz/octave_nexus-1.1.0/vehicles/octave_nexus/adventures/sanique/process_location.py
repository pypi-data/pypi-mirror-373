
''''
	from octave_nexus.adventures.sanique.process_location import find_sanic_process_location
	sanic_path = find_sanic_process_location ();
"'''

import shutil

#
#
#	need to import this for cx_freeze
#
#
import sanic

def find_sanic_process_location ():
	sanic_path = shutil.which ("sanic")

	if sanic_path is None:
		print ("Sanic executable not found. Please ensure it is installed.")
		sys.exit (1)

	print ("Found sanic process at:", sanic_path)

	return sanic_path


