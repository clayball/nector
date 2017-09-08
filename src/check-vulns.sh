#!/bin/bash

# check-vulns.sh by Brian Jopling, 2017
# ----------------------------------
# Checks that vulnlist.txt has been created and populated by user.
# If so, we're good. Otherwise, do it here.


if [[ -s ../vulnlist.csv ]]
then
    echo '[*] vulnlist.csv found and is populated.';
else
    touch ../vulnlist.csv
	echo '"Plugin","Plugin Name","Severity","IP Address","DNS Name"' > ../vulnlist.csv
fi
