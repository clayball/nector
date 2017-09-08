#!/bin/bash

# check-events.sh by Brian Jopling, 2017
# ----------------------------------
# Checks that events.txt has been created and populated by user.
# If so, we're good. Otherwise, do it here.


if [[ -s events.csv ]]
then
    echo '[*] events.csv found and is populated.';
else
    touch events.csv
	echo 'Request Number,Date Submitted,Title,Status,Last Edit Date,Submitted By,Assignees' > events.csv
fi
