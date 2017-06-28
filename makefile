# ===========================================================================
# Usage: $ make [run|demo]
# Prerequisites
#  hosts.xml, subnets.txt, vulnlist.csv, events.csv exist with data.
# Post-conditions
#  Performs migrations, imports data from above files to db.sqlite3, then runs
#  the NECTOR server.
# ===========================================================================

.PHONY : run

run :
	sudo pip install -r requirements.txt
	python manage.py makemigrations
	python manage.py migrate
	python import-data.py -v
	python import-ports.py
	python manage.py runserver


demo :
	cp -i sample-data/sample-hosts.xml hosts.xml
	cp -i sample-data/sample-vulnlist.csv vulnlist.csv
	cp -i sample-data/sample-events.csv events.csv
	sudo pip install -r requirements.txt
	python manage.py makemigrations
	python manage.py migrate
	python import-data.py
	python import-ports.py
	python manage.py runserver
