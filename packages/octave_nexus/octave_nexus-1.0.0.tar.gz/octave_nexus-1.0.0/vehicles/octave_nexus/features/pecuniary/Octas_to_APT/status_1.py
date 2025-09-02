

#
#	python3 health.proc.py "features/pecuniary/Octas_to_APT/status_1.py"
#
#

from octave_nexus.features.pecuniary.Octas_to_APT import convert_Octas_to_APT

from fractions import Fraction

def check_1_Octas ():
	OA_conversion = convert_Octas_to_APT ({
		"Octas": "1"
	})
	
	assert (OA_conversion ["victory"] == "yes"), OA_conversion;
	assert (OA_conversion ["APT"] == "0.00000001"), OA_conversion;


def check_2 ():
	OA_conversion = convert_Octas_to_APT ({
		"Octas": "0"
	})
	
	assert (OA_conversion ["victory"] == "yes"), OA_conversion;
	assert (OA_conversion ["APT"] == "0"), OA_conversion;

def check_3 ():
	OA_conversion = convert_Octas_to_APT ({
		"Octas": "-1"
	})
	
	assert (OA_conversion ["victory"] == "yes"), OA_conversion;
	assert (OA_conversion ["APT"] == "-0.00000001"), OA_conversion;


def check_4 ():
	OA_conversion = convert_Octas_to_APT ({
		"Octas": "-1123"
	})
	
	assert (OA_conversion ["victory"] == "yes"), OA_conversion;
	assert (OA_conversion ["APT"] == "-0.00001123"), OA_conversion;

def check_5 ():
	OA_conversion = convert_Octas_to_APT ({
		"Octas": "999999999"
	})
	
	assert (OA_conversion ["victory"] == "yes"), OA_conversion;
	assert (OA_conversion ["APT"] == "9.99999999"), OA_conversion;


def loss_1 ():
	OA_conversion = convert_Octas_to_APT ({
		"Octas": "0.1"
	})
	
	assert (OA_conversion ["victory"] == "no"), OA_conversion;
	assert (
		OA_conversion ["note"] == "The Octas amount must be greater than or equal to 1."
	), OA_conversion;
	
def loss_2 ():
	OA_conversion = convert_Octas_to_APT ({
		"Octas": ""
	})
	
	assert (OA_conversion ["victory"] == "no"), OA_conversion;
	assert (
		OA_conversion ["note"] == "The Octas amount could not be converted into a fraction."
	), OA_conversion;


checks = {
	'check 1, 1 Octa': check_1_Octas,
	'check 2, 0 Octas': check_2,
	'check 3, -1 Octas': check_3,
	'check 4, -1123 Octas': check_4,
	'check 5': check_5,
	
	'loss 1': loss_1,
	'loss 2': loss_2	
}