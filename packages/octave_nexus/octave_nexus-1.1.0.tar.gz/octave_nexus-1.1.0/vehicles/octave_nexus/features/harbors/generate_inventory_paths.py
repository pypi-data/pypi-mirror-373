




'''
	from foam.features.generate_inventory_paths import generate_inventory_paths
	inventory_paths = generate_inventory_paths (directory)
'''


'''
	https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types
'''


import glob
import os


translations = {
	"css": "text/css",
	"ico": "image/x-icon",
	"jpg": "image/jpg",		
	"js": "text/javascript",
	"json": "text/json",
	"html": "text/html",
	"png": "image/png",
	
	#
	#
	#	image/svg+xml
	#	image/svg
	#
	"svg": "image/svg+xml",
	
	
	"ttf": "font/ttf",

	"txt": "text/plain",
	"woff": "font/woff",
	"woff2": "font/woff2"
}


def generate_inventory_paths (directory):
	inventory_glob = directory + "/**/*"
	inventory = glob.glob (directory + "/**/*", recursive = True)
	
	inventory_partials = {}
	for inventory_path in inventory:
		print ("asset_path:", inventory_path);
	
		if (os.path.isfile (inventory_path)):
			FP = open (inventory_path, "rb")
			content = FP.read () 
			FP.close ()
		
			extension = inventory_path.split ('.')[-1].lower ()
			mime = "text/plain"
			
			if (extension in translations):
				mime = translations [ extension ]

			inventory_partials [ inventory_path.split (directory + "/") [1] ] = {
				"path": inventory_path,
				"content": content,
				"extension": extension,
				"mime": mime
			};
		
	return inventory_partials

