# ===========================================================================
# Usage: $ make [run|demo]
# Prerequisites
#  hosts.xml, openports.xml, vulnlist.csv, events.csv exist with data.
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


quick :
	pip install -r requirements.txt
	python manage.py makemigrations
	python manage.py migrate
	touch vulnlist.csv
	echo '"Plugin","Plugin Name","Severity","IP Address","DNS Name"' > vulnlist.csv
	echo ',,,,' >> vulnlist.csv
	touch events.csv
	echo 'Request Number,Date Submitted,Title,Status,Last Edit Date,Submitted By,Assignees' > events.csv
	echo ',,,,,,' >> events.csv
	./get-data.sh
	python import-data.py
	python manage.py runserver

demo :
	cp -i sample-data/sample-hosts.xml hosts.xml
	cp -i sample-data/sample-vulnlist.csv vulnlist.csv
	cp -i sample-data/sample-events.csv events.csv
	cp -i sample-data/sample-openports.xml openports.xml
	python manage.py makemigrations
	python manage.py migrate
	python import-data.py
	python manage.py runserver
