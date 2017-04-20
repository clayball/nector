#
# This makefile should only be run if you intend on using the
# sample files as your data. In essence, it's a way to quickly
# get NECTOR up and running.
#

.PHONY : run_demo

run_demo :
	mv -i sample-hosts.xml hosts.xml
	mv -i sample-subnets.txt subnets.txt
	mv -i sample-vulnlist.csv vulnlist.csv
	mv -i sample-report.csv report.csv
	python manage.py migrate
	python import-hosts.py
	python manage.py runserver
