# ===========================================================================
# Usage: $ make [run|demo]
# Prerequisites
#  hosts.xml, subnets.txt, vulnlist.csv, report.csv exist with data.
# Post-conditions
#  Performs migrations, imports data from above files to db.sqlite3, then runs
#  the NECTOR server.
# ===========================================================================

.PHONY : run

run :
	python manage.py makemigrations
	python manage.py migrate
	python import-data.py
	python manage.py runserver


demo :
	cp -i sample-hosts.xml hosts.xml
	cp -i sample-subnets.txt subnets.txt
	cp -i sample-vulnlist.csv vulnlist.csv
	cp -i sample-report.csv report.csv
	python manage.py migrate
	python import-data.py
	python manage.py runserver
