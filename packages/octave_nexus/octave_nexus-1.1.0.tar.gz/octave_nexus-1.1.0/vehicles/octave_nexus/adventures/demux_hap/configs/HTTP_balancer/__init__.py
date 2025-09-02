

'''
	import vessels.proxies.HA.configs.HTTP_balancer as HA_HTTP_balancer
	HA_HTTP_balancer.build (
		from_port = "80",
		to_addresses = [
			"0.0.0.0:8000",
			"0.0.0.0:8001"
		]
	)
'''

'''
	http://localhost:8404/stats
'''


"""
	backend servers
		balance roundrobin
		server server1 0.0.0.0:8000 maxconn 32
		server server2 0.0.0.0:8001 maxconn 32
"""

def build (
	from_port = "80",
	to_addresses = [],
	
	#
	#	roundrobin
	#
	balance = "leastconn",
	
	config_path = ""
):	
	'''
		examples:
			server server1 0.0.0.0:8000 check
			server server1 0.0.0.0:8001 check
	'''
	site_number = 1
	backend_sites = ""
	for to_address in to_addresses:
		name = "site_" + str (site_number)
		backend_sites += f"\tserver { name } { to_address } check\n"		
		site_number += 1


	config = f"""
global
	daemon
	maxconn 256

defaults
	mode http
	timeout connect 5000ms
	timeout client 50000ms
	timeout server 50000ms

frontend stats
	bind *:8404
	stats enable
	stats uri /stats
	stats refresh 10s
	stats admin if LOCALHOST

frontend http-in
	bind *:{ from_port }
	default_backend site
	
backend site
	balance { balance }
{ backend_sites }
"""

	if (len (config_path) >= 1):
		FP = open (config_path, "w")
		FP.write (config)
		FP.close ()
		
		print ("The config was written to:", config_path)

	return config;