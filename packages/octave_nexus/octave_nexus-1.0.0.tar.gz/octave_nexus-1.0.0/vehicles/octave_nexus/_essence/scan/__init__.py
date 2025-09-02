


'''
def run_script_move (script_name, function_name):
    try:
        # Import the script as a module
        script_module = importlib.import_module(script_name)
        
        # Access the function from the module
        func = getattr(script_module, function_name)
        
        # Execute the function
        func()
    except Exception as e:
        print(f"An error occurred: {e}")
'''

def scan_essence (essence_path):
	with open (essence_path, 'r') as file:
		script_content = file.read ()
        
	proceeds = {}	
		
	exec (script_content, {
		#'__file__': os.getcwd () + "/" + os.path.basename (file_path)
		'__file__': essence_path
	}, proceeds)
	
	essence = proceeds ['essence']
	
	return essence;