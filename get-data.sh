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
    ./get-hosts.sh;
    ./get-hops.sh;
else
    echo '[!] File subnets.txt not found or is empty!';
    echo '[!] Creating subnets.txt and prompting user...';
    touch subnets.txt;
    echo '# List of Subnets' >> subnets.txt;
    echo '# Add your subnet(s) or individual hosts here.' >> subnets.txt;
    echo '# ------------------------' >> subnets.txt;
    echo '0.0.0.0/24 #(Follow this format for subnets and delete this line before saving)' >> subnets.txt;
    echo '0.0.0.0 #(Follow this format for hosts and delete this line before saving)' >> subnets.txt
    vi subnets.txt;
    ./get-hosts.sh;
    ./get-hops.sh;
fi
