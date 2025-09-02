

import shutil
def has_sanic_check ():
	the_path = shutil.which ("sanic")

	if the_path is not None:
		return True;
	
	raise Exception ("'sanic' not found in path")

