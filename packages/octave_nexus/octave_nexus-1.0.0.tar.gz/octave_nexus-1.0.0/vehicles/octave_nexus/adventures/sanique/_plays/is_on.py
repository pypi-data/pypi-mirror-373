
'''
	sanic inspect shutdown
'''

'''	
	from vaccines.adventures.sanique._controls.is_on import check_sanique_status
	the_sanic_status = check_sanique_status ()
'''


	
	

#/
#
from biotech.topics.show.variable import show_variable
#
#
import requests
import rich
#
#
import multiprocessing
import subprocess
import time
import os
import atexit
#
#\


def check_sanique_status (packet = {}):
	#harbor_port = int (packet ["ports"] ["harbor"])
	inspector_port = str (packet ["ports"] ["inspector"])

	def actually_check ():
		host = "0.0.0.0"
		port = inspector_port
		
		URL = f"http://{ host }:{ port }"
		
		try:
			response = requests.get (URL)
			if response.status_code == 200:
				data = response.json ()

				return "on"
			
			else:
				print ("Error:", response.status_code)
		
		except Exception as E:
			print ("sanique status check exception:", E)

		return "off"
		
	return actually_check