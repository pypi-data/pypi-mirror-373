

''''
	@ open sign
"'''

''''
	Sanic:

@guest_addresses.route ("/")
	async def home (request):
		if check_allow_proceed_sanique (request.cookies) != "yes":
			return send_rules_sanique (sanic_response)
"'''

''''
	Flask:
		from octave_nexus.features.harbor_locations.rules_form import (
			check_allow_proceed_flask,
			send_rules_flask
		)
		
		if check_allow_proceed_flask () != "yes":
			return send_rules_flask ()
"'''

from flask import Flask, request, Response

def check_allow_proceed_flask ():
    try:
        allow_proceed = request.cookies.get ('allow_proceed')
        if allow_proceed == "yes":
            return "yes"
    
    except Exception as E:
        print ("allow proceed exception:", E)
    
    return "no"

def send_rules_flask ():
	return Response (
        rules_form ({}),
        content_type = "text/html",
        headers = {}
    )

def check_allow_proceed_sanique (cookies):
	try:
		allow_proceed = cookies.get ('allow_proceed')
		if allow_proceed == "yes":
			return "yes"
			
	except Exception as E:
		print ("allow proceed exception:", E)
			
	return "no"

def send_rules_sanique (sanic_response):
	return sanic_response.raw (
		rules_form ({}), 
		content_type = "text/html",
		headers = {}
	)


def rules_form (packet):
	return """
<html>
<head>
	<style>
		p {
			padding: 5px 0;
			margin: 0;
		}
	
	</style>
</head>
<body
	style="
		display: flex;
		justify-content: center;
		align-content: center;
		flex-direction: column;
	
		box-sizing: border-box;
		margin: 0;
		padding: 1cm;
		
		height: 100vh;
		width: 100vw;
		
		overflow-y: scroll;
		
		background: #EEF;
	"
>
	<main
		monitor="memo"
		style="
			margin: 0 auto;
			max-width: 15cm;
		"
	>	
		<div
			style="
				height: fit-content;
				width: 100%;
				
				padding: 1cm;
				border-radius: 0.25cm;
				
				background: #FFF;
				border: 2px solid #000;
			"
		>
			<header
				style="
					font-size: 1.4em;
					text-align: center;
				"
			>Memo</header>
			
			<header
				style="
					font-size: 1.2em;
					text-align: center;
				"
			>
				<span>Domain: </span>
				<span id="domain"></span>
			</header>
			
			<div style="height: 1cm"></div>
			
			<div>
				<header
					style="
						font-weight: bold;
						font-size: 1.3em;
					"
				>This domain requires:</header>		
				<ul>
					<li>links to sub domains</li>
					<li>links to other domains</li>
					<li>storing envelopes in the browser</li>
				</ul>
			</div>
			

			<div style="height: 0.5cm"></div>

			<div
				style="
					line-height: 100%;
				"
			>
				<header
					style="
						font-weight: bold;
						font-size: 1.3em;
						padding-bottom: 0.5cm;
					"
				>Appropriateness:</header>		
				<p>This domain is intended to be appropriate for most audiences.</p>
				<p>Interactions are limited to approved places on the Aptos web.</p>
				<p>Extension wallet content is subject to external discretion.</p>
			</div>

			<div style="height: 0.5cm"></div>
			
			<div
				style="
					text-align: right;
				"
			>
				<button 
					monitor="proceed button"
				
					onclick="proceed_tapped ()"
					
					style="
						background: #b6b6d5;
						color: black;
						cursor: pointer;
						
						padding: 0.25cm 0.5cm;
						border-radius: 0.25cm;
						border: 2px solid #a570ca;
						
						font-size: 1em;
					"
				>Accept</button>
			</div>
		</div>
	</main>
	
	<script>
		var store_cookie = (name, value) => {
			const expires = "; expires=Fri, 31 Dec 9999 23:59:59 GMT";
			document.cookie = name + "=" + (value || "") + expires + "; path=/";
		}

		var proceed_tapped = () => {
			store_cookie ("allow_proceed", "yes");
			location.reload ();
		}
		
		document.addEventListener("DOMContentLoaded", function() {
			var domain = window.location.hostname;
			console.log (domain);
			
			document.getElementById ("domain").textContent = domain;
		});
	</script>
</body>	
	"""

