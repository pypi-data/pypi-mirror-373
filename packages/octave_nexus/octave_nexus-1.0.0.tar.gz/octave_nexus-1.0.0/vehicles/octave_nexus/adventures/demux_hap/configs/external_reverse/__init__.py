



'''
	import vessels.proxies.HA.SSL as HA_SSL
	HA_SSL.build_papers (
		certificate_path = "/etc/haproxy/SSL/certificate.pem",
		key_path = "/etc/haproxy/SSL/certificate.pem.key"
	)

	import vessels.proxies.HA.configs.external_reverse as HA_external_reverse
	HA_external_reverse.build_config (
		start = "yes",

		SSL_certificate_path = "/etc/haproxy/SSL/certificate.pem",
		config_path = "/etc/haproxy/haproxy.cfg",
		
		external_HTTPS_port = "443",
		external_HTTP_port = "80",
		
		to_addresses = [
			"0.0.0.0:8000",
			"0.0.0.0:8000",
			"0.0.0.0:8000",
			"0.0.0.0:8000",
			"0.0.0.0:8000",
			"0.0.0.0:8000",
			"0.0.0.0:8000",
			"0.0.0.0:8000"
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



def build_config (
	start = "no",

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

frontend stats
	bind *:8404
	stats enable
	stats uri /stats
	stats refresh 10s
	stats admin if LOCALHOST

#
#	https://www.haproxy.com/documentation/haproxy-configuration-tutorials/ssl-tls/
#
#	frontend www
#	frontend www
#
frontend www
	mode http
	bind :80
	bind :443 ssl crt { SSL_certificate_path }
	http-request redirect scheme https unless { ssl_fc }
	default_backend sites

#
#	option forwardfor -> X-Forwarded-For
#
backend sites
	balance { balance }
	option forwardfor
{ backend_sites }	
	
'''

	if (len (config_path) >= 1):
		FP = open (config_path, "w")
		FP.write (config)
		FP.close ()
		
		print ("The config was written to:", config_path)

	if (start == "yes"):
		import os
		os.system (f"haproxy -f '{ config_path }' -c")
		os.system ("systemctl restart haproxy")
		os.system (f"cat '{ config_path }'")
		os.system ("systemctl status haproxy -l --no-pager")

	return config