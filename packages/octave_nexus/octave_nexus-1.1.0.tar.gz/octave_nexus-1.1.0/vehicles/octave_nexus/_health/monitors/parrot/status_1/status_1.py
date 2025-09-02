


''''
octave_nexus_1 parrot check_EQ \
--origin "/Metro/vehicles/octave_nexus/_health/monitors/parrot/status_1/example_equality/directory_1" \
--to "/Metro/vehicles/octave_nexus/_health/monitors/parrot/status_1/example_equality/directory_2"
"'''

''''
octave_nexus_1 parrot check_EQ \
--origin "/Metro/vehicles/octave_nexus/_health/monitors/parrot/status_1/example_inequality/directory_1" \
--to "/Metro/vehicles/octave_nexus/_health/monitors/parrot/status_1/example_inequality/directory_2"
"'''

''''
octave_nexus_1 parrot equalize \
--origin "/Metro/vehicles/octave_nexus/_health/monitors/parrot/status_1/example_equality" \
--to "/Metro/vehicles/octave_nexus/_health/monitors/parrot/status_1/example_equality_2"

octave_nexus_1 parrot check_EQ \
--origin "/Metro/vehicles/octave_nexus/_health/monitors/parrot/status_1/example_equality" \
--to "/Metro/vehicles/octave_nexus/_health/monitors/parrot/status_1/example_equality_2"
"'''

''''
	TODO:
		octave_nexus parrot equalize
		octave_nexus parrot check_EQ
		
		__glossary/octave_nexus_1
"'''
def check_1 ():
	return;



checks = {
	'check 1': check_1
}