



##
#

#
#
##


#/
#
import click
#
#
from octave_nexus.adventures.sanique.venture import sanique_venture
from octave_nexus.adventures.demux_hap.venture import demux_hap_venture
#
#
from octave_nexus._essence import retrieve_essence
#
#
from ventures import ventures_map
#
#\


from octave_nexus.adventures.harbor_basin import turn_on_harbor
from octave_nexus._essence import turn_off_external_essence
	

def ventures_group ():
	# essence = retrieve_essence ()

	@click.group ("harbor")
	def group ():
		pass;
	
	
	@group.command ("open")
	def command__health ():	
		turn_off_external_essence ()
		turn_on_harbor ({});
	
	
	return group;






#



