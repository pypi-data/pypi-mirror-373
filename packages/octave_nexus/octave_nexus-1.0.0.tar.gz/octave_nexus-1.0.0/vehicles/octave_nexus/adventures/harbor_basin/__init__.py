

''''
	from octave_nexus.adventures.harbor_basin import turn_on_harbor
"'''

''''
	TODO:
		* Allow CORS
		* 
"'''


#/
#
from octave_nexus._essence import retrieve_essence
from octave_nexus.features.harbors.generate_inventory_paths import generate_inventory_paths
from octave_nexus.features.harbor_locations.rules_form import (
	check_allow_proceed_flask,
	send_rules_flask
)
#
#
import sanic
from sanic import Sanic
from sanic_ext import openapi
import sanic.response as sanic_response
#
#
import json
from os.path import exists, dirname, normpath, join
from urllib.parse import unquote
import threading
import time
from fractions import Fraction
#
#\


from flask import Flask, send_file, Response, jsonify


turn_on_caching = "no"

def turn_on_harbor (packet):
	if ("port" in packet):
		port = packet ["port"]
	else:
		port = 2300;

	essence = retrieve_essence ()

	app = Flask(__name__)

	##/
	build_path = essence ["sveltnetics"] ["build_path"];
	the_index = build_path + "/index.html"
	the_assets = build_path + "/assets"
	
	front_inventory_paths = generate_inventory_paths (build_path)
	for front_path in front_inventory_paths:
		print ("front_path:", front_path)
		pass;
	##\


	@app.route ('/')
	def home ():
		if check_allow_proceed_flask () != "yes":
			return send_rules_flask ()
		
		print ("home");
		
		return send_file (the_index);
		
		#return await sanic_response.file (the_index)

	@app.route ("/<path:path>")
	def assets_route (path):
		if check_allow_proceed_flask () != "yes":
			return send_rules_flask ()
			
	
		the_path = False
		try:
			the_path = f"{ path }"
			if (the_path in front_inventory_paths):
				content_type = front_inventory_paths [ the_path ] ["mime"]
				content = front_inventory_paths [ the_path ] ["content"]
				
				#print ("content:", content)
				
				headers = {}
				if (turn_on_caching == "yes"):
					headers ["Custom-Header-1"] = "custom"
					headers ["Cache-Control"] ="private, max-age=31536000"
					
					#"Expires": "0"
				
				'''
				return sanic_response.raw (
					content, 
					content_type = content_type,
					headers = headers
				)
				'''				
				response = Response (
					content, 
					content_type = content_type, 
					headers = headers
				)
				
				return response;
				
		except Exception as E:
			print ("E:", E)
		
			response = jsonify ({
				"note": "An anomaly occurred while processing.",
				"the_path": the_path
			})
			response.status_code = 600  # Custom status code (201 Created)
			#response.headers['X-Custom-Header'] = 'CustomValue'  # Custom header
			
			return response
			
			''''
			return sanic_response.json ({
				"note": "An anomaly occurred while processing.",
				"the_path": the_path
			}, status = 600)
			"'''
		
		return send_file (the_index);
		#return await sanic_response.file (the_index)

	app.run (
		host = '0.0.0.0', 
		port = port,
		#debug = True
	)