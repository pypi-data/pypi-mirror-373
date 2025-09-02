

#----
#
from .build import build_demux_certificates
#
#
import click
#
#----

def demux_hap_clique ():
	@click.group ("demux_hap")
	def group ():
		pass

	@group.command ("build_unverified_certificates")
	def build_unverified_certificates ():
		print ("build_unverified_certificates")
		build_demux_certificates ()

	return group




#






