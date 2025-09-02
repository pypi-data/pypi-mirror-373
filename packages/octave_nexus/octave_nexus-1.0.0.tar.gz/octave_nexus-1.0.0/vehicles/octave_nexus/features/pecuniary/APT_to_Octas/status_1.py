

#
# python3 health.proc.py "features/pecuniary/APT_to_Octas/status_1.py"
#
#

from octave_nexus.features.pecuniary.APT_to_Octas import convert_APT_to_Octas

from fractions import Fraction

def check_1 ():
	AO_conversion = convert_APT_to_Octas ({
		"APT": "1"
	})
	
	assert (AO_conversion ["victory"] == "yes");
	assert (AO_conversion ["Octas"] == "100000000");
	assert (AO_conversion ["Octas"] == str (Fraction ("1e8")));
	
def check_2 ():
	AO_conversion = convert_APT_to_Octas ({
		"APT": "0.00000001"
	})
	
	assert (AO_conversion ["victory"] == "yes");
	assert (AO_conversion ["Octas"] == "1");

def check_3 ():
	APT = "112312312312312312312312341723491283749812734123123123.12312378"
	Octas = "11231231231231231231231234172349128374981273412312312312312378"

	AO_conversion = convert_APT_to_Octas ({
		"APT": APT
	})
	
	assert (Fraction (APT) == Fraction (Octas) * 8)
	assert (AO_conversion ["victory"] == "yes");
	assert (AO_conversion ["Octas"] == Octas);

def loss_1 ():
	AO_conversion = convert_APT_to_Octas ({
		"APT": "0.000000001"
	})
	
	assert (AO_conversion ["victory"] == "no");
	assert (AO_conversion ["note"] == "The APT amount must be more than 0.00000001");
	

def loss_2 ():
	AO_conversion = convert_APT_to_Octas ({
		"APT": "0"
	})
	
	assert (AO_conversion ["victory"] == "no");
	assert (AO_conversion ["note"] == "The APT amount must be more than 0.00000001");
	

def loss_3 ():
	AO_conversion = convert_APT_to_Octas ({
		"APT": "-1.0"
	})
	
	assert (AO_conversion ["victory"] == "no");
	assert (AO_conversion ["note"] == "The APT amount must be more than 0.00000001");

def loss_4 ():
	AO_conversion = convert_APT_to_Octas ({
		"APT": ""
	})
	
	assert (AO_conversion ["victory"] == "no");
	assert (AO_conversion ["note"] == "The APT amount could not be converted into a fraction.");

def loss_5 ():
	AO_conversion = convert_APT_to_Octas ({
		"APT": "1.123412343"
	})
	
	assert (AO_conversion ["victory"] == "no");
	assert (AO_conversion ["note"] == "The APT amount can't have more than 8 digits after the decimal point.");



checks = {
	'1e8 Octas': check_1,
	'1 Octa': check_2,
	
	'APT to Octas: loss 1': loss_1,
	'APT to Octas: loss 2': loss_2,
	'APT to Octas: loss 3': loss_3,
	'APT to Octas: loss 4': loss_4
}