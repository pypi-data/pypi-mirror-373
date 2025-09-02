



'''
	from vaccines.adventures.sanique.adventure import sanique_adventure
	sanique_adventure ()
'''

#
#
from octave_nexus._essence import retrieve_essence
#
#
from ._plays.on import turn_on_sanique
from ._plays.off import turn_off_sanique
from ._plays.is_on import check_sanique_status
#
#

def sanique_venture ():
	essence = retrieve_essence ()
	
	harbor_port = essence ["sanique"] ["port"]
	inspect_port = essence ["sanique"] ["inspector"] ["port"]

	return {
		"name": "sanique",
		"kind": "task",
		"turn on": {
			"adventure": turn_on_sanique ({
				"ports": {
					"harbor": harbor_port,
					"inspector": inspect_port
				}
			}),
		},
		"turn off": turn_off_sanique ({
			"ports": {
				"inspector": inspect_port
			}
		}),
		"is on": check_sanique_status ({
			"ports": {
				"inspector": inspect_port
			}
		})
	}