#!/usr/bin/env python3

''' Small program to test resolvers and show their status with respect to draft-ietf-dnsop-kskroll-sentinel '''

import subprocess, argparse

# This program is used to test resolvers for whether they implement draft-ietf-dnsop-kskroll-sentinel.
#    The results are visual: that is, there is no conformance test.
#    Please post issues and proposed updates on https://github.com/paulehoffman/sentinel-testbed

# In the following list, the resolvers in 165.254.24.* are hosted on a best-effort basis,
#   and are not to be considered "definitive". Please contact paul.hoffman@icann.org
#   if you have questions about them
resolvers_to_try = [
	["Google public DNS", "8.8.8.8"],
	["Quad9 secure", "9.9.9.9"],
	["Cloudflare managed DNS", "1.1.1.1"],
	["Yandex.DNS Basic", "77.88.8.8"],
	["Unbound 1.7.1", "165.254.24.232"],
	["BIND 9.12.1 good", "165.254.24.234"],
	["BIND 9.12.1 bad", "165.254.24.235"]
]

servers_to_try = [
	["is-ta", "root-key-sentinel-is-ta-20326.sentinel.research.icann.org"],
	["not-ta", "root-key-sentinel-not-ta-20326.sentinel.research.icann.org"],
	["bogus", "bogus.sentinel.research.icann.org"],
]

dig_template = "dig +time=3 +noanswer +noauthority +noquestion +noadditional +noedns +nostats"
header_signal = "->>HEADER<<-" 
def dig_this(name, res_address):
	''' Returns a string indicating the status of a "dig" request to a resolver '''
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
	# Here is none of teh lines had the header_signal in them
	if "connection timed out" in dig_lines[-1]:
		return "connection timed out"
	else:
		return "unknown error"

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("resolver_to_test", nargs="*", help="One or more resolver names or addresses")
	cli = parser.parse_args()
	# Add names from the command line to the list of tests
	if cli.resolver_to_test:
		for (i, this_cli_arg) in enumerate(cli.resolver_to_test):
			resolvers_to_try.append(["Command line option {} - {}".format(i+1, this_cli_arg), this_cli_arg ])

	collected_results = {}  # Holder for the overall results
	for this_resolver_pair in resolvers_to_try:
		(this_resolver_name, this_resolver_address) = this_resolver_pair
		print("Starting {}".format(this_resolver_name))
		collected_results[this_resolver_name] = {}  # Store the results for this name
		for this_server_pair in servers_to_try:
			(this_server_type, this_name) = this_server_pair
			this_status = dig_this(this_name, this_resolver_address)
			# Expected statuses will have a comma in them
			#   Save both the true/false value needed by the draft, as well as the status for possible later work
			if "," in this_status:
				this_status = this_status.replace(",", "")
				if this_status in ("NOERROR"):
					collected_results[this_resolver_name][this_server_type] = [ True, this_status ]
				elif this_status in ("NXDOMAIN", "SERVFAIL"):
					collected_results[this_resolver_name][this_server_type] = [ False, this_status ]
				else:
					exit("Got unexpected status {} when querying {} for {}. Exiting.".format(this_status, this_name, this_resolver_address))
			else:
				if this_status == "connection timed out":
					exit("Got a timeout on {} for {}. Exiting.".format(this_name, this_resolver_address))
				elif header_signal in this_status:
					exit("Got unexpected HEADER line {} when querying {} for {}. Exiting.".format(this_status, this_name, this_resolver_address))

	for this_resolver_pair in resolvers_to_try:
		(this_resolver_name, this_resolver_address) = this_resolver_pair
		this_is_ta = collected_results[this_resolver_name]["is-ta"][0]
		this_not_ta = collected_results[this_resolver_name]["not-ta"][0]
		this_bogus = collected_results[this_resolver_name]["bogus"][0]
		# The following is the logic from the draft
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
