

#----
#
import pathlib
from os.path import dirname, join, normpath
import sys
import os
#
#
import pydash
#
#----

def establish_alerts_allowed (alert_level):
	alert_ranks = [ "scholar", "info", "caution", "emergency", "front" ]

	alert_found = False;
	allow_alerts = []
	for alert_rank in alert_ranks:
		if (alert_level == alert_rank):
			alert_found = True;
			
		# print ("alert_rank:", alert_rank, alert_level, alert_level == alert_rank)			
			
		if (alert_found):
			allow_alerts.append (alert_rank)
			
	# print ("allow_alerts:", allow_alerts)		
	
	return allow_alerts

def merge_essence (external_essence, essence_path):
	this_directory = pathlib.Path (__file__).parent.resolve ()	
	the_mix_directory = str (normpath (join (this_directory, "../..")));
	
	essence_directory = str (normpath (join (essence_path, "..")));
	
	'''
		"onsite": {
			"host": "0.0.0.0",
			"port": "39000",
			
			"path": crate ("monetary_1/data"),
			"logs_path": crate ("monetary_1/logs/the.logs"),
			"PID_path": crate ("monetary_1/the.process_identity_number"),
		}
	'''
	the_merged_essence = pydash.merge (
		{
			"essence_path": essence_path,
			
			"the_mix_directory": the_mix_directory,
			
			"ventures": {
				"path": str (normpath (join (
					essence_directory, 
					"octave_nexus_ventures_map.JSON"
				)))
			},
			
			#
			#	summary in goodest.mixes.activate_alert
			#
			"alert_level": "caution",
			
			#
			#	modes: [ "nurture", "business" ]
			#
			"mode": "business",
			
			"CWD": os.getcwd (),
			
			"sveltnetics": {
				"build_path": str (normpath (join (
					the_mix_directory, 
					"sveltnetics_packets"
				)))
			},
			
			"demux_hap": {
				"build self signed certs": "no",
				"to": "0.0.0.0:22000"
			},
			
			#
			#
			#	web:	This is where "sanic" process is available.
			#
			#	dist:
			#
			"sanique_mode": "web",
			
			"sanique": {
				"directory": str (normpath (join (
					the_mix_directory, 
					"adventures/sanique"
				))),
				
				"path": str (normpath (join (
					the_mix_directory, 
					"adventures/sanique/harbor/on.proc.py"
				))),
				
				"port": "22000",
				"host": "0.0.0.0",
				
				#
				#	don't modify these currently
				#
				#	These are used for retrieval, but no for launching the
				#	sanic inspector.
				#
				#	https://sanic.dev/en/guide/running/inspector.md#inspector
				#
				"inspector": {
					"port": "22001",
					"host": "0.0.0.0"
				}
			},
			"dictionary": {
				"path": str (normpath (join (the_mix_directory, "__glossary"))),
				"goodest": str (normpath (join (the_mix_directory, "__glossary/goodest"))),
			}
		},
		external_essence
	)
	
	
	
	the_merged_essence ["allowed_alerts"] = establish_alerts_allowed (
		the_merged_essence ["alert_level"]
	)
	
	print ("allowed alerts", the_merged_essence ["allowed_alerts"])

	
	return the_merged_essence