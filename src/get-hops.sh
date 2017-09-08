#!/bin/bash

# get-hops.sh by Brian Jopling, 2017
# ----------------------------------
# Reads each line of our Nmap scan found in hosts.xml and parses out the
# IP address for hosts that are up. Performs a traceroute on that IP address
# and saves the results to a file called hops.csv.
#
# Note: The first column of each line contains the IP address that is being
# tracerouted to. This makes it easier for parsing and interpretting the data.
# The following lines refer to each hop.
#
# Ex Results.
#    8.8.8.8,example.com(1.2.3.4),google.com(8.8.8.8)
#    8.8.8.8                   ,  example.com(1.2.3.4) , google.com(8.8.8.8)
#    ^ IP we want to traceroute,  ^first hop           , ^next hop


rm hops.csv >/dev/null       # Remove the file if it exists. (Easy way to clear the results)
touch hops.csv >/dev/null    # Create the file if it doesn't exist.

# Iterate through each line of file. Each line stored in $host.
while IFS= read -r host;
do
    # Get the IP addr and remove surrounding parenthesis.
    ip=$(echo $host | awk '{print $6}' | tr --delete '(' | tr --delete ')');
    # Ensure it is an IP addr. This is a weak form of validation, it
    # only checks if $ip consists of nums, periods, and spaces,
    # but this is all we need as long as our nmap scans stay consistent.
    if [[ $ip =~ [0-9\.\b]. ]] ;
    then
        echo '[*] Performing traceroute on' $ip;
        # Perform traceroute and parse hops into csv format.
        # First column of each line will be the IP tracerouted to.
        $(traceroute $ip | awk -F ' ' '{print $2 $3}' | xargs | sed -e 's/ /,/g' | cut -d ',' -f1- | cut -c 3- >> hops.csv);
    fi
done < hosts.xml # Use hosts.xml as file to read from throughout the loop.

# Inform user that we're done.
echo ''
echo '[!] Complete. See file: hops.csv';
