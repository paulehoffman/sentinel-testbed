#!/usr/bin/env python3

import subprocess, argparse

resolvers_to_try = [
	["Google public DNS", "8.8.8.8"],
	["Quad9 secure", "9.9.9.9"],
	["Cloudflare managed DNS", "1.1.1.1"],
	["Unbound 1.7.1", "165.254.24.232"],
	["BIND 9.12.1 good", "165.254.24.234"],
	["BIND 9.12.1 bad", "165.254.24.235"],
	["Yandex.DNS Basic", "77.88.8.8"]
]

servers_to_try = [
	["is-ta", "root-key-sentinel-is-ta-20326.sentinel.research.icann.org"],
	["not-ta", "root-key-sentinel-not-ta-20326.sentinel.research.icann.org"],
	["bogus", "bogus.sentinel.research.icann.org"],
]

dig_template = "dig +time=3 +noanswer +noauthority +noquestion +noadditional +noedns +nostats"
header_signal = "->>HEADER<<-" 
def dig_this(name, res_address):
	''' Returns a string indicating the status '''
	dig_lines = subprocess.getoutput("{} @{} {}".format(dig_template, res_address, name)).splitlines()
	for this_line in dig_lines:
		if header_signal in this_line:
			line_parts = this_line.split(" ")
			try:
				status_name_loc = line_parts.index("status:")
			except:
				return this_line  # Return the whole line so that it appears in the exit message
			else:
				return line_parts[status_name_loc + 1]			

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("resolver_to_test", nargs="*", help="One or more resolver names or addresses")
	cli = parser.parse_args()
	if cli.resolver_to_test:
		for (i, this_cli_arg) in enumerate(cli.resolver_to_test):
			resolvers_to_try.append(["Command line option {}".format(i), this_cli_arg ])

	collected_results = {}

	for this_resolver_pair in resolvers_to_try:
		(this_resolver_name, this_resolver_address) = this_resolver_pair
		print("Starting {}".format(this_resolver_name))
		collected_results[this_resolver_name] = {}  # Store the results
		for this_server_pair in servers_to_try:
			(this_server_type, this_name) = this_server_pair
			this_status = dig_this(this_name, this_resolver_address)
			this_status = this_status.replace(",", "")
			if this_status in ("NXDOMAIN", "SERVFAIL"):
				collected_results[this_resolver_name][this_server_type] = [ False, this_status ]
			elif this_status == "NOERROR":
				collected_results[this_resolver_name][this_server_type] = [ True, "NOERROR" ]
			else:
				if header_signal in this_status:
					exit("Got unexpected HEADER line {} when querying {} for {}. Exiting.".format(this_status, this_name, this_resolver_address))
				else:
					exit("Got unknow status {} when querying {} for {}. Exiting.".format(this_status, this_name, this_resolver_address))

	for this_resolver_pair in resolvers_to_try:
		(this_resolver_name, this_resolver_address) = this_resolver_pair
		this_is_ta = collected_results[this_resolver_name]["is-ta"][0]
		this_not_ta = collected_results[this_resolver_name]["not-ta"][0]
		this_bogus = collected_results[this_resolver_name]["bogus"][0]
		status = ""		
		if (this_is_ta and not(this_not_ta) and not(this_bogus)):
			status = "Vnew"
		elif (not(this_is_ta) and this_not_ta and not(this_bogus)):
			status = "Vold"
		elif (this_is_ta and this_not_ta and not(this_bogus)):
			status = "Vleg"
		elif (this_is_ta and this_not_ta and this_bogus):
			status = "nonV"
		else:
			status = "other"
		print("{}: {}".format(this_resolver_name, status))
		if status == "other":
			print("   This is 'other' because is-ta {},  not-ta {}, bogus {}".format(this_is_ta, this_not_ta, this_bogus))
