



#/
#
from octave_nexus._essence import retrieve_essence
#
from octave_nexus.features.pecuniary.APT_to_Octas import convert_APT_to_Octas
from octave_nexus.features.pecuniary.Octas_to_APT import convert_Octas_to_APT#
#
import sanic
from sanic import Sanic
from sanic_ext import openapi
import sanic.response as sanic_response
from sanic_limiter import Limiter, get_remote_address
#
#
import json
from os.path import exists, dirname, normpath, join
from urllib.parse import unquote
import threading
import time
from fractions import Fraction
#
#\_




def regions_math (vue_regions_packet):
	essence = retrieve_essence ()
	
	app = vue_regions_packet ["app"]
	
	math_addresses = sanic.Blueprint ("math", url_prefix = "/math")
	app.blueprint (math_addresses)
	
	@math_addresses.route ("/APT_to_Octas", methods=["PATCH"])
	async def address_APT_to_Octas (request):
		try:
			data = request.json
			
			AO_conversion = convert_APT_to_Octas ({
				"APT": data ["APT"]
			})
			if (AO_conversion ["victory"] != "yes"):
				return sanic_response.json ({
					"victory": "no",
					"note": AO_conversion ["note"]
				}, status = 600)
				
			return sanic_response.json ({
				"victory": "yes",
				"Octas": AO_conversion ["Octas"]
			}, status = 200)
			
		except Exception as E:
			return sanic_response.json ({
				"victory": "no",
				"note": "An exception occurred: " + str (E)
			}, status = 600)
		
		
	@math_addresses.route ("/Octas_to_APT", methods = ["PATCH"])
	async def address_Octas_to_APT (request):
		try:
			data = request.json
			
			OA_conversion = convert_Octas_to_APT ({
				"Octas": data ["Octas"]
			})
			if (OA_conversion ["victory"] != "yes"):
				return sanic_response.json ({
					"victory": "no",
					"note": OA_conversion ["note"]
				}, status = 600)
				
			return sanic_response.json ({
				"victory": "yes",
				"Octas": OA_conversion ["Octas"]
			}, status = 200)
			
		except Exception as E:
			return sanic_response.json ({
				"victory": "no",
				"note": "An exception occurred: " + str (E)
			}, status = 600)
	
	

	