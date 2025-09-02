
''''
from octave_nexus.features.pecuniary.Octas_to_APT import convert_Octas_to_APT
OA_conversion = convert_Octas_to_APT ({
	"Octas": "1"
})
"'''

from fractions import Fraction
from decimal import Decimal, getcontext

def remove_trailing_zeros (the_string):
	if ('.' in the_string):
		return str (the_string).rstrip ('0').rstrip ('.')
	
	return the_string


def convert_Octas_to_APT (packet):
	try:
		if ("greater_than_zero" in packet):
			greater_than_zero = packet ["greater_than_zero"]
		else:
			greater_than_zero = "no"
		

		if ("Octas" not in packet):
			return {
				"victory": "no",
				"note": "An Octas amount was not added to the ask."
			}
			
		
		if (type (packet ["Octas"]) not in [ str, int ]):
			return {
				"victory": "no",
				"note": "The Octas amount needs to be a string or an integer."
			}

		try:
			Octas = Fraction (packet ["Octas"])
		except Exception:
			return {
				"victory": "no",
				"note": "The Octas amount could not be converted into a fraction."
			}
		
		APT = Octas / Fraction ("1e8")
		
		#
		#	This implies the Octas amount is not an integers.
		#
		#
		if (Octas.denominator != 1):
			return {
				"victory": "no",
				"note": "The Octas amount must be greater than or equal to 1."
			}
		
		if (greater_than_zero == "yes"):	
			Minimum_APT = (Fraction ("1") / Fraction ("1e8"));
			if (APT < Minimum_APT):
				return {
					"victory": "no",
					"note": "The APT amount must be more than 0.00000001"
				}
		
		APT_String = remove_trailing_zeros (f"{ float (APT) :.8f}")
		print ("APT float:", APT_String)
		
		
		if (Fraction (APT_String) != APT):
			return {
				"victory": "no",
				"note": "A math error occurred while transforming the APT fraction to a decimal string."
			}
		
		return {
			"victory": "yes",
			"APT": APT_String
		}
		
	except Exception as E:
		print ("exception:", E)
		
	return {
		"victory": "no",
		"note": "An exception occurred while converting the Octas amount to the APT amount."
	}