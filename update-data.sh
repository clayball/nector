#!/bin/bash

# update-data.sh by Brian Jopling, 2017
# ----------------------------------
# Calls get-data.sh, which will update hosts.xml, openports.xml, and hops.csv.
# Then imports this new data into the database.

echo '[*] Getting updated hosts / ports / hops...'
src/get-data.sh;
echo '[*] Importing updated data into database...'
python import-data.py;
echo '[!] Complete!'
