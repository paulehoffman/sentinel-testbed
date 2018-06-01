#!/usr/bin/env python3
''' Creates the web page that has three different ways to test the client side of draft-ietf-dnsop-kskroll-sentinel '''

# The text for the index page
index_text = '''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html lang="en"><head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
</head>
<body>

<!-- The JavaScript on this page shows three different ways to preform the client side of draft-ietf-dnsop-kskroll-sentinel -->

<!-- Before running the tests, create holders for the positive results from the three tests, and define the tests -->
<script>
var labels_found = { "jsfetch": [], "imgfetch": [], "jqfetch": [] };
// Holders for the results of the tests
var results_found = { "jsfetch": [], "imgfetch": [], "jqfetch": [] };
</script>

<!-- Test style 1: Success is based on filling in the "jsfetch" object from scripts as they are called.
Create an object, then fill the object from external scripts 
Inspired by Paul Hoffman. -->
<script>var jsfetch = {};</script>
<script src="http://root-key-sentinel-is-ta-20326.$$DOMAINBASE$$/is-ta.js"></script>
<script src="http://root-key-sentinel-not-ta-20326.$$DOMAINBASE$$/not-ta.js"></script>
<script src="http://bogus.$$DOMAINBASE$$/bogus.js"></script>

<!-- Test style 2: Success is based on fetching images and filling in the "imgfetch" object by
checking the resulting height (0 means not fetched).
Inspired by Warren Kumari. -->
<p hidden>
<img id="imgfetch_is_ta" src="http://root-key-sentinel-is-ta-20326.$$DOMAINBASE$$/tiny.gif"/>
<img id="imgfetch_not_ta" src="http://root-key-sentinel-not-ta-20326.$$DOMAINBASE$$/tiny.gif"/>
<img id="imgfetch_bogus" src="http://bogus.$$DOMAINBASE$$/tiny.gif"/>
</p>
<script>
if (imgfetch_is_ta.height > 0) { labels_found["imgfetch"].push("is-ta") }
if (imgfetch_not_ta.height > 0) { labels_found["imgfetch"].push("not-ta") }
if (imgfetch_bogus.height > 0) { labels_found["imgfetch"].push("bogus") }
</script>

<!-- Test style 3: Success is based on resolving URLs with XMLHttpRequest via jQuery and filling 
in the "jqfetch" object based on if there was a result.
Inspired by Ray Bellis and Noah Ross. -->
<script src="https://code.jquery.com/jquery-3.3.1.js"></script>
<script>
// It doesn't matter what the file type is if we use the HEAD method
var jqfetch_urls = {
	"is-ta": "http://root-key-sentinel-is-ta-20326.$$DOMAINBASE$$/tiny.gif",
	"not-ta": "http://root-key-sentinel-not-ta-20326.$$DOMAINBASE$$/tiny.gif",
	"bogus": "http://bogus.$$DOMAINBASE$$/tiny.gif"
};
var jq_types_finished = [];  // A holder for the URL requests have finished (even if the URL could not be fetched)
// The following is launched in window.onload
function jqfetch_request(this_type) {
	$.ajax({ url: jqfetch_urls[this_type], type: "HEAD" })
	.done(function() { labels_found["jqfetch"].push(this_type) })
	.always(function() {
		jq_types_finished.push(this_type);
		// Only do the summarizing after all the URLs are completed
		if (jq_types_finished.length === Object.keys(jqfetch_urls).length) {
			// Get the summary
			results_found["jqfetch"] = sentinel_summary("jqfetch");
			// Call calculate_status here instead at the top level of a later script because the queries are async
			calculate_status();
		}
	})
}
</script>

<!-- Calculate results and push them into some text for display -->
<script>
// Returns an array of (array of the labels found, text of the status)
function sentinel_summary(in_array) {
	// Make the kskroll-sentinel logic more readable
	var these_labels = labels_found[in_array]
	this_is_ta = (these_labels.indexOf("is-ta") > -1);
	this_not_ta = (these_labels.indexOf("not-ta") > -1);
	this_bogus = (these_labels.indexOf("bogus") > -1);
	var status = "";
	if (this_is_ta && !this_not_ta && !this_bogus) { status = "Vnew" }
	else if (!this_is_ta && this_not_ta && !this_bogus) { status = "Vold" }
	else if (this_is_ta && this_not_ta && !this_bogus) { status = "Vind" }
	else if (this_is_ta && this_not_ta && this_bogus) { status = "nonV" }
	else { status = "other" }
	return [ these_labels, status ];
}
// Finds the status from the three objects, compares them, and fills in the status_text id for later display
function calculate_status(){
	// Collect the status results into a temporary array status_results so we can compare them
	var status_results = [];
	for (this_test in results_found) { status_results.push(results_found[this_test][1]) }
	// See if each result matches the first result
	if (status_results.every(function(x) { return x === status_results[0] })) {
		status_text.innerHTML = "<p>The status for all " + Object.keys(status_results).length + " tests was &ldquo;" + status_results[0] + "&rdquo;</p>\\n";
	} else {
		status_text.innerHTML = "<p>The statuses of the " + Object.keys(status_results).length + " tests differ. They were:\\n<ul>";
		for (this_test in results_found) { status_text.innerHTML += "<li>" + this_test + ": " + results_found[this_test][1] + "</li>\\n" }
		status_text.innerHTML += "</ul></p>\\n";
	}
}
// Launch the test when the window is loaded
window.onload = function() {
	results_found["jsfetch"] = sentinel_summary("jsfetch");
	results_found["imgfetch"] = sentinel_summary("imgfetch");
	for (var this_type in jqfetch_urls) { jqfetch_request(this_type) }
}
</script>

<!-- Display the results in the page -->
<!-- For a real test program, this would include a lot of explanatory text, not just the status -->
<span id=status_text />
</body></html>
'''

# Fix the domain names in the index_text
domain_base = "sentinel.research.icann.org"  ### This will obviously change for different test environments
index_text = index_text.replace("$$DOMAINBASE$$", domain_base)

# Be sure the output file doesn't already exist
import os
if os.path.exists("index.html"):
	exit("index.html already exists, so not over-writing. Exiting.")
	
# Write out the index file
f_out = open("index.html", mode="wt")
f_out.write(index_text)
f_out.close()
print("Wrote out new index.html file")
print("Don't forget to copy bogus.js, is-ta.js, not-ta.js, and tiny.gif\n   into the web directory when you copy the index.html file there")
