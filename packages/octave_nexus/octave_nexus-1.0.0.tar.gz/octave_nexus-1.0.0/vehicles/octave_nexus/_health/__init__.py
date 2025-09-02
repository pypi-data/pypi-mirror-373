
#----
#
import Emergency
#
#
import rich
#
#
import json
import pathlib
from os.path import dirname, join, normpath
import os
import sys
import subprocess
#
#----

def monitor_health (packet = {}):
	#glob_string = packet ["glob_string"]
	#vehicles = packet ["vehicles"]
	#this_vehicle = packet ["this_vehicle"]
	#db_directory = packet ["db_directory"]
	
	if ("argv" in packet):
		argv = packet ["argv"]
	else:
		argv = []

	name = "octave_nexus"
	this_directory = pathlib.Path (__file__).parent.resolve ()

	vehicles = "/Metro/vehicles"
	this_vehicle = str (normpath (join (vehicles, f"octave_nexus")))

	if (len (argv) >= 2):
		glob_string = this_vehicle + '/' + argv [1]
		db_directory = False
	else:
		glob_string = this_vehicle + '/**/status_*.py'
		db_directory = normpath (join (this_directory, "DB"))

	print ("glob string:", glob_string)

	promote = Emergency.on ({
		"glob_string": glob_string,
		
		"simultaneous": True,
		"simultaneous_capacity": 50,

		"time_limit": 60,

		"module_paths": [
			vehicles
		],

		"relative_path": this_vehicle,
		
		"db_directory": db_directory,
		
		"aggregation_format": 2
	})


	promote ["off"] ()



	#
	#	This is a detailed report
	#	of the technique.
	#
	rich.print_json (data = {
		"paths": promote ["proceeds"] ["paths"]
	})

	#
	#	This is the checks that did 
	#	not finish successfully.
	#
	rich.print_json (data = {
		"alarms": promote ["proceeds"] ["alarms"]
	})

	#
	#	This is concise stats about
	#	the  technique.
	#
	rich.print_json (data = {
		"stats": promote ["proceeds"] ["stats"]
	})