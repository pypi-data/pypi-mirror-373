
''''
	
"'''


'''
	leaps:
		[ ] build the certificates
		[ ] retrieve and build the processes
		[ ] 
'''

import octave_nexus.adventures.demux_hap.SSL as HA_SSL

def build_demux_certificates ():
	HA_SSL.build_papers (
		certificate_path = "/etc/haproxy/SSL/certificate.pem",
		key_path = "/etc/haproxy/SSL/certificate.pem.key"
	)