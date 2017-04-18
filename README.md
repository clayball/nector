# NECTOR - by haX0rs for haX0rs

![nector home](nector-home.png)

## About NECTOR

NECTOR is an open source successor to the HECTOR project, both of which have
been sponsored by the University of Pennsylvania School of Arts & Sciences.

The purpose of NECTOR is to increase security awareness among institutions
by demonstrating potential security vulnerabilities. NECTOR is a powerful and
expandable framework used in the collection, analysis, and sharing of security
intelligence information.

NECTOR takes advantage of the functionality and stability of the Django
framework, and incorporates a SQLite database backend with a minimalistic
frontend. The project is being developed without the use of JavaScript.

NECTOR's intuitive web-based frontend allows for easy data analysis, scan
configuration, incident reporting,  and more. 

## Misc. Notes

Lets try to stick with Python2 for now.

This is the main NECTOR project repo.

We'll be adding small applications to this project over time.

Applications:

- hosts (subnets)
- detection
- osint
- events
- reports

## Installing

View INSTALL.txt for more info.

## Getting Started

Create a virtualenv to work in and activate it.

'''
$ virtualenv-2 venv-nector
$ source venv-nector/bin/activate
$ pip install < requirements.txt
'''

Apply the migrations. TODO: explain this

```$ python manage.py migrate```


Start the server.

'''$ python manage.py runserver'''


Open a browser and goto 127.0.0.1:8000

When you're done working run ```$ deactivate```.

TODO: remove: Testing for issue #8.. will remove.

## Events

TODO: Add more to this section.

- An event is an observed change to the normal behavior of a system, environment, process, workflow or person. Examples: router ACLs were updated, firewall policy was pushed.
- An alert is a notification that a particular event (or series of events) has occurred, which is sent to responsible parties for the purpose of spawning action. Examples: the events above sent to on-call personnel.
- An incident is a human-caused, malicious event that leads to (or may lead to) a significant disruption of business. Examples: attacker posts company credentials online, attacker steals customer credit card database, worm spreading through network.*

