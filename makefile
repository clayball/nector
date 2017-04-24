#
# Usage: $ make
# Pre-conditions: hosts.xml, subnets.txt, vulnlist.csv, and report.csv exist with wanted data.
# Post-conditions: Performs migrations, imports data from above files to db.sqlite3, then runs the NECTOR server.
#

.PHONY : run

run :
	python manage.py makemigrations
	python manage.py migrate
	python import-hosts.py
	python manage.py runserver
