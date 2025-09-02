

#/
#
import importlib
import os
from os.path import dirname, join, normpath
import sys
import pathlib
from pathlib import Path
#
#
import click
#
#
from octave_nexus.adventures.ventures import retrieve_ventures
#
#
#from ventures.clique import ventures_clique
#from octave_nexus.mixes._clique import mixes_clique
#
#
from .group import clique as clique_group
from .parrot import parrot as parrot_group
from .ventures import ventures_group
#
#\


from octave_nexus._health import monitor_health


#mixes_clique = importlib.import_module ("octave_nexus.mixes._clique").mixes_clique

def build (essence_path):
	essence = """

essence = {}
	
	"""
	
	with Path (essence_path).open ('w') as FP:
		FP.write (essence)

def clique ():
	@click.group ()
	def group ():
		pass

	
	#\
	#
	#	/octave_nexus
	#		/[records]
	#		octave_nexus_essence.py
	#
	@click.command ("build")
	def command__build ():	
		CWD = os.getcwd ()
		
		essence_path = str (normpath (join (CWD, "octave_nexus_essence.py")))
		build (essence_path);
		print ("built", essence_path)

	group.add_command (command__build)
	#
	#/

	#\
	#
	@click.command ("health")
	def command__health ():	
		CWD = os.getcwd ()
		
		print ("health")
		
		monitor_health ();

	group.add_command (command__health)
	#
	#/
	
	#/
	#
	#	This raises an exception if the "octave_nexus_essence.py" is not yet built.
	#
	#
	try:
		from ventures.clique import ventures_clique
		group.add_command (ventures_clique ({
			"ventures": retrieve_ventures ()
		}))
		
		''''
		group.add_command (importlib.import_module ("ventures.clique").ventures_clique ({
			"ventures": retrieve_ventures ()
		}))
		"'''
		
		from octave_nexus.adventures.demux_hap._plays._clique import demux_hap_clique
		group.add_command (demux_hap_clique ())
		
	except Exception as E:
		print ("venture import exception:", E)
	
	group.add_command (parrot_group ())
	group.add_command (ventures_group ())
	
	group ()




#
