

'''
	from octave_nexus.adventures.demux._controls.is_on import check_if_demux_hap_is_on
'''

#++++
#
import octave_nexus.adventures.demux_hap.SSL as HA_SSL
import octave_nexus.adventures.demux_hap.configs.HTTPS_to_HTTP as HA_HTTPS_to_HTTP
#
#
import os
#
#
import requests
#
#++++

def check_if_demux_hap_is_on ():
	haproxy_endpoint = "https://0.0.0.0:443"
	
	try:
		response = requests.get (haproxy_endpoint, timeout = 1, verify = False)
		
		print ("response:", response)
		
		if response.status_code >= 100:
			return "on"
			
	except requests.RequestException as e:
		print ("HAProxy request exception:", e)
		
	return "off"
