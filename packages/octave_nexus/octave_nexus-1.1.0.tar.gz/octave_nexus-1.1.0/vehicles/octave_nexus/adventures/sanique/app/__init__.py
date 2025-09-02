
#/
#
from ..harbor.regions_sockets import regions_sockets
from ..harbor.regions_guests import regions_guests
from ..harbor.regions_math import regions_math
#
from octave_nexus._essence import retrieve_essence, build_essence
from octave_nexus.adventures.alerting import activate_alert
from octave_nexus.adventures.alerting.parse_exception import parse_exception
#
#
import sanic
from sanic import Sanic
from sanic_ext import openapi, Extend
import sanic.response as sanic_response
#
#
import json
import os
import traceback
#
#\_


def create_1 ():
	essence = retrieve_essence ()
	inspector_port = essence ["sanique"] ["inspector"] ["port"]
	

	print ("""

		Sanique
		
		
	""");

	app = Sanic ("sanique")

	app.config.OAS_UI_SWAGGER = False
	
	''''
	app.extend (config = {
		"oas_url_prefix": "/docs",
		"swagger_ui_configuration": {
			"docExpansion": "list" # "none"
		},
	})
	"'''
	
	app.config.INSPECTOR = True
	app.config.INSPECTOR_HOST = "0.0.0.0"
	app.config.INSPECTOR_PORT = int (inspector_port)
	
	
	
	#
	#	https://sanic.dev/en/plugins/sanic-ext/http/cors.html#configuration
	#
	#
	@app.middleware ('response')
	async def before_route_middleware (request, response):
		URL = request.url
		response.headers['Access-Control-Allow-Origin'] = '*'
		response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
		response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
		response.headers['Access-Control-Allow-Credentials'] = 'true'
		
		print ('Obtained an ask for:', URL)
		#print ('headers', response.headers)
	
	
	
	#
	#	opener
	#
	#
	app.ext.openapi.add_security_scheme ("api_key", "http")
	
	
	regions_guests ({ "app": app })
	regions_math ({ "app": app })

	return app