
'''
	from octave_nexus.adventures.sanique._ops.off import turn_off_sanique
	turn_off_sanique ()
'''


'''
	sanic inspect shutdown
'''


'''
	objectives:
		[ ] implicit
'''

#----
#
#
import multiprocessing
import subprocess
import time
import os
import atexit
#
#----

def background (procedure):
	process = subprocess.Popen (procedure)


def refresh_sanique (packet):
	inspector_port = str (packet ["ports"] ["inspector"])

	process = background (
		procedure = [
			"sanic",
			"inspect",
			"reload",
			
			f"--port",
			inspector_port,
		]
	)
	
