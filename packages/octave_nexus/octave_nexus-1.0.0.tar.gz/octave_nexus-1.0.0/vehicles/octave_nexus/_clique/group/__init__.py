


def clique ():
	import click
	@click.group ("example-group")
	def group ():
		pass


	import click
	@group.command ("course-1")
	@click.option ('--example-option', required = True)
	def search (example_option):
		print ("example_option:", example_option)
	
		retrun;

	return group




#



