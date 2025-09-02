

'''
	from vaccines.adventures.sanique._controls.on as turn_on_sanique
	turn_on_sanique ()
'''


'''
	sanic /vaccines/venues/stages/vaccines/adventures/sanique/harbor/on.proc.py
'''

#/
#
import atexit
import json
import multiprocessing
from multiprocessing import Process
import subprocess
import time
import os
import shutil
import sys
import time
import threading
import pathlib
from os.path import dirname, join, normpath
import sys
#
#
from ventures.utilities.hike_passive_forks import hike_passive_forks
from octave_nexus._essence import retrieve_essence
#
#\


from octave_nexus.adventures.sanique.process_location import find_sanic_process_location
		


def turn_on_sanique_web (packet):
	essence = retrieve_essence ()

	harbor_port = int (packet ["ports"] ["harbor"])
	inspector_port = str (packet ["ports"] ["inspector"])

	def actually_turn_on ():
		harbor_path = str (normpath (join (
			pathlib.Path (__file__).parent.resolve (), 
			".."
		))) 
		
		env_vars = os.environ.copy ()
		env_vars ['PYTHONPATH'] = ":".join (sys.path)
		env_vars ['inspector_port'] = inspector_port
		env_vars ['essence_path'] = essence ["essence_path"]

		
		#sanic_process = "sanic"
		sanic_process = find_sanic_process_location ();
		
		script = [
			sanic_process,
			f'harbor:create',
			f'--port={ harbor_port }',
			f'--host=0.0.0.0',
			'--factory',
			'--fast'
		]
		
		#
		#
		#	Without this, the server might stop when 
		#	SSH connection is disconnected.
		#
		#
		if (essence ["mode"] == "business"):
			script.append ("--no-access-logs")
			script.append (">")
			script.append ('/dev/null')
			script.append ('&')
		
		
		hike_passive_forks ({
			"script": " ".join (script),
			"Popen": {
				"cwd": harbor_path,
				"env": env_vars,
				"shell": True
			}
		})


	return actually_turn_on;



def turn_on_sanique (packet = {}):
	return turn_on_sanique_web (packet);
	
