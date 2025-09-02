
'''
	from octave_nexus.adventures.demux_hap.venture import demux_hap_venture
	demux_hap_venture ()
'''

from ._plays.on import turn_on_demux_hap
from ._plays.off import turn_off_demux_hap
from ._plays.is_on import check_if_demux_hap_is_on

def demux_hap_venture ():
	return {
		"name": "demux_hap",
		"kind": "task",
		"turn on": {
			"adventure": turn_on_demux_hap,
		},
		"turn off": turn_off_demux_hap,
		"is on": check_if_demux_hap_is_on
	}

