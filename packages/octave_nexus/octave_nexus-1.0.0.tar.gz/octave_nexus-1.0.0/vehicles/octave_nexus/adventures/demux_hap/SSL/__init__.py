

'''
import vessels.proxies.HA.SSL as HA_SSL
HA_SSL.build_papers (
	certificate_path = "/etc/haproxy/SSL/certificate.pem",
	key_path = "certificate.pem.key"
)
'''

import os

from os.path import dirname, join, normpath
import pathlib
import sys

def build_papers (
	certificate_path = "",
	key_path = "",
	
	days = "20000"
):
	assert (len (certificate_path) >= 1);
	assert (len (key_path) >= 1);
	
	certificate_path_dir = normpath (join (certificate_path, ".."))
	key_path_dir = normpath (join (key_path, ".."))
	
	make_dirs = [
		f"mkdir -p '{ certificate_path_dir }'",
		f"mkdir -p '{ key_path_dir }'"
	]
	
	print (make_dirs [0])
	print (make_dirs [1])	
	
	os.system (f"mkdir -p '{ certificate_path_dir }'")
	os.system (f"mkdir -p '{ key_path_dir }'")
	
	script = " ".join ([
		"openssl req -x509 -newkey rsa:4096",
		f"-keyout '{ key_path }'",
		f"-out '{ certificate_path }'",
		f'-sha256 -days { days } -nodes -subj "/C=/ST=/L=/O=/OU=/CN="'
	])

	

	os.system (script)
	
	return;