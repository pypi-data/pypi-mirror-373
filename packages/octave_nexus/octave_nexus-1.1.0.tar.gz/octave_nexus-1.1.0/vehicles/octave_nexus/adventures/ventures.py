




'''
	from octave_nexus.adventures.ventures import retrieve_ventures
	the_ventures = retrieve_ventures ()
'''

#/
#
from .sanique.venture import sanique_venture
from .demux_hap.venture import demux_hap_venture
#
#
from octave_nexus._essence import retrieve_essence
#
#
from ventures import ventures_map
#
#\

def retrieve_ventures ():
	essence = retrieve_essence ()

	return ventures_map ({
		"map": essence ["ventures"] ["path"],
		"ventures": [
			demux_hap_venture (),
			sanique_venture ()
		]
	})