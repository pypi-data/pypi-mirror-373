


'''
	import vessels.proxies.HA.configs.HTTPS_to_HTTPS as HA_HTTPS_to_HTTPS
	HA_HTTPS_to_HTTPS.build (
		to_addresses = [
			"0.0.0.0:8000",
			"0.0.0.0:8001"
		]
	)
'''

'''
	frontend mywebsite
    mode http
    bind :80
    bind :443 ssl crt /etc/ssl/certs/ssl.pem
    default_backend servers
'''



def build (
	

	to_addresses = [],

	#
	#	roundrobin
	#
	balance = "leastconn",

	SSL_certificate_path = "",
	config_path = ""
):

	ssl_fc = "{ ssl_fc }"

	site_number = 1
	backend_sites = ""
	for to_address in to_addresses:
		name = "site_" + str (site_number)
		backend_sites += f"\tserver { name } { to_address } check\n"		
		site_number += 1

	config = f'''
	
global
	daemon
	maxconn 256

defaults
	mode http
	timeout connect 5000ms
	timeout client 50000ms
	timeout server 50000ms

#
#	https://www.haproxy.com/documentation/haproxy-configuration-tutorials/ssl-tls/
#
#	frontend www
#	frontend www
#
frontend www
	mode http
	bind *:80
	bind :443 ssl crt "{ SSL_certificate_path }"
	http-request redirect scheme https unless { ssl_fc }
	default_backend site
	

backend site
	balance { balance }
{ backend_sites }		
	
	
'''

	if (len (config_path) >= 1):
		FP = open (config_path, "w")
		FP.write (config)
		FP.close ()
		
		print ("The config was written to:", config_path)

	return config