

import click
import ships.paths.directory.rsync as rsync
import ships.paths.directory.check_equality as check_equality

import json
import pprint

def parrot ():
	@click.group ("parrot")
	def group ():
		pass

	
	@group.command ("check_EQ")
	@click.option ('--origin', required = True)
	@click.option ('--to', required = True)
	def search (origin, to):
		report = check_equality.start (
			origin,
			to
		)	
		
		pprint.pprint ({
			"equality check report": report
		})
		
		assert (
			report ==
			{'1': {}, '2': {}}
		)
		
		
	
		return;
		
	@group.command ("equalize")
	@click.option ('--origin', required = True)
	@click.option ('--to', required = True)
	def search (origin, to):
		rsync.process ({
			"from": origin,
			"to": to,
			
			#
			#	if "no", return the process script, but don't run it
			#
			#	if "yes", start rsync
			#
			"start": "yes",
			
			
			#
			#
			#	Maybe: if "yes", restart rsync on change to "to"
			#
			#
			"sense": "no"
		})
		
		report = check_equality.start (
			origin,
			to
		)	
		
		pprint.pprint ({
			"equality check report": report
		})
		
		assert (
			report ==
			{'1': {}, '2': {}}
		)

	return group




#



