


'''
	from goodest.adventures.alerting.parse_exception import parse_exception
	parse_exception (E)
'''

import io
import sys
import traceback

def parse_exception (exception : Exception) -> str:
	try:
		file = io.StringIO ()
		traceback.print_exception (exception, file = file)
		
		return file.getvalue ().rstrip ()
	except Exception as E2:
		print (E2)
		pass;
		
	try:
		return str (exception)
	except Exception as E3:
		print (E3)
		pass;
		
	return "An exception occurred that could not be parsed."