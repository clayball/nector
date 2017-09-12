#!/bin/bash

# get-data.sh by Brian Jopling, 2017
# ----------------------------------
# Checks that subnets.txt has been populated by user.
# If so, calls the scripts `get-hosts.sh` and `get-hops.sh`.
# get-hosts.sh will create hosts.xml and openports.xml.
# get-hops.sh will create hops.csv.


if [[ -s subnets.txt ]]
then
    echo '[*] subnets.txt found and is populated.';
    src/get-hosts.sh;
    src/get-hops.sh;
    src/check-vulns.sh;
    src/check-events.sh;
else
    echo '[!] File subnets.txt not found or is empty!';
    echo '[!] See the README for more info.';
fi
