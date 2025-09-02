



''''
from octave_nexus.features.pecuniary.APT_to_Octas import convert_APT_to_Octas
AO_conversion = convert_APT_to_Octas ({
	"APT": "1"
})
"'''

from fractions import Fraction

def convert_APT_to_Octas (packet):
	try:
		if ("APT" not in packet):
			return {
				"victory": "no",
				"note": "An APT amount was not added to the ask."
			}
			
		
		if (type (packet ["APT"]) not in [ str, int ]):
			return {
				"victory": "no",
				"note": "The APT amount needs to be a string or an integer."
			}
		
		try:
			APT = Fraction (packet ["APT"])
		except Exception:
			return {
				"victory": "no",
				"note": "The APT amount could not be converted into a fraction."
			}

		
		
		Minimum_APT = (Fraction ("1") / Fraction ("1e8"));
		if (APT < Minimum_APT):
			return {
				"victory": "no",
				"note": "The APT amount must be more than 0.00000001"
			}
		
		Octas = Fraction (APT) * Fraction ("1e8");
		if (Octas.denominator != 1):
			return {
				"victory": "no",
				"note": "The APT amount can't have more than 8 digits after the decimal point."
			}
		
		return {
			"victory": "yes",
			"Octas": str (Octas)
		}
		
	except Exception:
		return {
			"victory": "no",
			"note": "An exception occurred while converting the Octas amount into the APT amount."
		}