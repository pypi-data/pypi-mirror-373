
''''
	Python3 PyPI pips:
		requirements map:
			pip install pipdeptree
		
			pipdeptree --json-tree
			
		include LICENSE with pip:
			https://pypi.org/project/pip-licenses/
		
			pip-licenses --with-license-file --format=plain > licenses.txt
			
			pip-licenses --with-license-file --format=json > /Metro/vehicles/octave_nexus/Rules/Laboratory/PyPI_tenets_full.json
			pip-licenses > /Metro/vehicles/octave_nexus/Rules/Laboratory/PyPI_tenets_outline.txt
			
		check why a dependency exists?
			pip install pipdeptree
			pipdeptree > imports_tree.txt
"'''



''''
	JavaScript + NPM

		generate-license-file
			.glf.cjs

		/*
			To figure out why a module is used:
				(cd /Metro/vehicles_frontend/sveltenetics && npm ls rc)
		*/

		/*
			relevant:
				license-report
				license-checker
		*/

"'''