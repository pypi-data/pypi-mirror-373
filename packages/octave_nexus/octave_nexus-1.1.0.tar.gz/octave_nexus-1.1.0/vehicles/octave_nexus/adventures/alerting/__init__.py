

'''
	from goodest.adventures.alerting.parse_exception import parse_exception
	from goodest.adventures.alerting import activate_alert
	activate_alert ("emergency", {
		"exception": parse_exception (E)
	})
	
	activate_alert ("info", "", mode = "condensed")
'''

'''
	from goodest.adventures.alerting import activate_alert
	activate_alert ("front", {}, mode = "pprint")
	activate_alert ("emergency", {}, mode = "condensed")
'''

'''
	levels:
		"front"
			[ "front" ]
	
			This means that this is some text or visual that
			is requested to be displayed in the terminal.
	
		"emergency"
			[ "emergency", "front" ]
		
		"caution"
			[ "emergency", "caution" ]
		
		"info"
			 [ "emergency", "caution", "info" ]
		
		"scholar"
			[ "emergency", "caution", "info", "scholar" ]
'''

'''
	{
		"line": 
		"file": 
	}
'''


#/
#
from octave_nexus._essence import retrieve_essence
#
#
import rich
from rich.console import Console
#
#
import inspect
from pprint import pprint
import sys
import traceback
#
#\

def activate_alert (level, variable, mode = "rich"):
	essence = retrieve_essence ()
	allowed_alerts = essence ["allowed_alerts"]
	if (level not in allowed_alerts):
		return;
	
	filename = "?"
	lineno = "?"
	try:
		try:
			raise Exception ()
		except:
			exc_type, exc_value, exc_traceback = sys.exc_info ()
			
			try:
				filename = exc_traceback.tb_frame.f_back.f_code.co_filename
			except Exception:
				pass;
				
			try:
				lineno = exc_traceback.tb_frame.f_back.f_lineno
			except Exception:
				pass;

		if (mode == "pprint"):
			pprint ({
				"level": level,
				"variable": variable,
				"path": filename,
				"line": lineno,
			})
		
		elif (mode == "condensed"):
			console = Console()
			
			with console.capture () as capture:
				console.print (variable, end = "")

			output_string = capture.get()			
			print (f"[{ level }] { filename }:{ lineno }: " + output_string)
		
		elif (mode == "show"):
			rich.print ({
				"level": level,
				"variable": variable,
				"path": filename,
				"line": lineno
			})
		
		else:		
			rich.print_json (data = {
				"level": level,
				"variable": variable,
				"path": filename,
				"line": lineno
			})
			
	except Exception as E:
		print ("variable printing exception:", E)
	
		try:
			rich.print_json (data = {
				"level": level,
				"variable printing exception details:": {
					"path": filename,
					"line": lineno
				}
			})
			
		except Exception as E2:
			print ("exception in variable printing details exception:", E2)

