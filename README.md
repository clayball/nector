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


---


## Getting Started


### Setting up a Virtual Environment (Recommended)

Create a [virtualenv](https://virtualenv.pypa.io/en/stable/) to work in, and
activate it.

```
$ virtualenv venv-nector
$ source venv-nector/bin/activate
```


### Downloading Dependencies

Install [pip](https://pypi.python.org/pypi/pip) dependencies.

```
$ pip install -r requirements.txt
```


### Trying the Demo (Optional)

If you want to try out the demo of NECTOR before making a full
commitment, run:

```
$ make demo
```

Then, open a browser and go to **http://127.0.0.1:8000**

If you like what you see, delete the sample database and move on to the next step.

```
$ rm db.sqlite3
```


### Choosing a Database

NECTOR is configured to work with three types of RDBMSs easily: **SQLite3**, **MySQL**, and **PostgreSQL**.

SQLite3 is light-weight, server-less, and requires practically no configuration. However, a SQLite3 database stores its information in a single binary file, and imposes limits on its users when querying a large amount of data.

MySQL is a popular, large-scale database server that's easy to setup, and features lots of third-party support,
expansive functionality for its users, and reads / writes data very quickly. Although, some functionalities get handled
a bit less-reliably with MySQL than other RDBMSs, and MySQL does not adhere to SQL compliancy rules.

PostgreSQL is much more server-friendly, featuring high concurrency and the ability to deal with large datasets. Though, it does need to be set up and configured, which may pose as a nuisance toward someone wanting to use NECTOR out of the box. It features
tons of bells and whistles, gearing it toward advanced RDBMS users.

Ideally, if you intend on hosting NECTOR on a public-facing server, MySQL or PostgreSQL should be your choice.
Otherwise, if you're working locally or only dealing with a small amount of traffic, SQLite3 will work great.

[If you're still unsure which RDMBS you should use, checkout this DigitalOcean article.](https://www.digitalocean.com/community/tutorials/sqlite-vs-mysql-vs-postgresql-a-comparison-of-relational-database-management-systems)

#### Setting up a SQLite3 Database (Option A)

1. No manual setup required for a SQLite3 database.


#### Setting up a MySQL Database (Option B)

1. Install necessary components.

    ```
    $ sudo dnf install mysql mysql-server MySQL-python
    ```

2. Start MySQL on boot. (Optional)

    ```
    $ chkconfig --levels 235 mysqld on
    ```

3. Start MySQL process.

    ```
    $ service mysqld start
    ```

4. Get MySQL dependency through pip.

    ```
    pip install mysql-python
    ```

5. Create a database and a database user.

    ```
    $ mysql -u root -p
    $ CREATE DATABASE nector CHARACTER SET UTF8;
    $ CREATE USER myuser@localhost IDENTIFIED BY 'password123';
    $ GRANT ALL PRIVILEGES ON nector.* TO myuser@localhost;
    $ FLUSH PRIVILEGES;
    $ exit
    ```

6. Modify project settings to use your database.

    ```
    $ vi nector/settings.py
    ```
    Find the 'DATABASE' section and replace it with:

    ```
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'nector',
            'USER': 'myuser',
            'PASSWORD': 'password123',
            'HOST': 'localhost',
            'PORT': '3306',
            'ATOMIC_REQUESTS': True,
        }
    }
    ```

    Make sure you change the NAME, USER, PASSWORD, and PORT sections to fit your needs!


#### Setting up a PostgreSQL Database (Option C)

1. Install necessary components.

    ```
    $ sudo dnf install postgresql postgresql-contrib postgresql-devel postgresql-server
    ```


2. Get PostgreSQL dependency through pip.

    ```
    pip install psycopg2
    ```

3. Create a database and a database user.

    ```
    $ sudo su - postgres
    $ psql
    $ CREATE DATABASE nector;
    $ CREATE USER myuser WITH PASSWORD 'password123';
    $ ALTER ROLE myuser SET client_encoding TO 'utf8';
    $ ALTER ROLE myuser SET default_transaction_isolation TO 'read committed';
    $ ALTER ROLE myuser SET timezone TO 'EST';
    $ GRANT ALL PRIVILEGES ON DATABASE nector TO myuser;
    $ \q
    $ exit
    ```

4. Modify project settings to use your database.

    ```
    $ vi nector/settings.py
    ```
    Find the 'DATABASE' section and replace it with:

    ```
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'nector',
            'USER': 'myuser',
            'PASSWORD': 'password123',
            'HOST': 'localhost',
            'PORT': '',
            'ATOMIC_REQUESTS': True,
        }
    }
    ```

    Make sure you change the USER and PASSWORD sections to fit your needs!


### Using Your Secret Key

Traverse into the nector/ subdirectory and open settings.py in a text editor.

```
$ vi nector/settings.py
```

Find the line

    SECRET_KEY = 'THISISTOPSECR3t,MAN!'

and replace it with your own Django secret key.

[Click here to obtain a Secret Key.](http://www.miniwebtool.com/django-secret-key-generator/)


### Initializing the Database

Django uses [migrations](https://docs.djangoproject.com/en/1.11/topics/migrations/)
to keep track of changes to the database's tables.

First, create new migrations based on the Django models of your project.

```
$ python manage.py makemigrations
```

Next, apply the migrations to your database (this will create a database if
one does not already exist). Doing this will fill your database with the tables
you need for the project.

```
$ python manage.py migrate
```


### Creating Your Data


#### Getting Hosts with Nmap

Create a file `subnets.txt` and fill it with your subnets.

```
$ vi subnets.txt
```

Use [nmap](https://nmap.org/) to run a scan on all the hosts in those subnets.
Save this scan as hosts.xml

```
$ nmap -sL -iL subnets.txt -oN hosts.xml
```

#### Getting Vulnerabilities with Nessus

Go into Nessus.

Under the _Analysis_ dropdown, select _Vulnerabilities_.

From the new dropdown box in the top left corner, select _Vulnerability List_.

In the top right corner, click on the _Options_ dropdown, and select
_Export as CSV_.

Make sure _only_ 'Plugin ID', 'Plugin Name', 'Severity', 'IP Address', and
 'DNS Name' are selected.

Click submit, and save this file as _vulnlist.csv_ in your NECTOR root directory.


#### Getting Events

Todo.


#### Getting Ports

If you haven't already, create a file `subnets.txt` and fill it with your subnets.

```
$ vi subnets.txt
```

Use [nmap](https://nmap.org/) to run a popular-ports scan on all the hosts in your subnets.

Save this scan as openports.xml

```
$ nmap -Pn -sV --version-light -vv -T5 -p17,19,21,22,23,25,53,80,123,137,139,153,161,443,445,548,636,1194,1337,1900,3306,3389,4380,4444,4672,5353,5900,6000,6881,8000,8080,9050,31337 -iL subnets.txt --open -oX openports.xml 2>&1 > /dev/null
```

This scan may take some time to complete.


#### Filling in the Gaps

If you were unable to perform any of the above four steps, keep reading.
Otherwise, you should skip this step.

Copy the sample data you need from `sample-data/` into this project's root folder.

```
$ cp sample-data/MISSING-FILE .
```

Note that you will have to remove the _sample-_ prefix from each file.

Missing Hosts:
```
$ cp sample-data/sample-hosts.xml hosts.xml
```

Missing Ports:
```
$ cp sample-data/sample-openports.xml openports.xml
```

Missing Vulnerabilities:
```
$ cp sample-data/sample-vulnlist.csv vulnlist.csv
```

Missing Events:
```
$ cp sample-data/sample-events.csv events.csv
```

Edit the file(s) to use your data.

Do not mess up the formatting!


### Populating the Database

In order to use your data, you will have to import it into the database.

```
$ python import-data.py
```


### Running NECTOR

Start the server.

```
$ python manage.py runserver
```

Open a browser and go to **http://127.0.0.1:8000**


### Deactivating the Virtual Environment

If you set up a Virtual Environment, run `$ deactivate` once you're done
working on NECTOR.


### The Makefile

The makefile exists to automate making migrations and importing
data.

If you make frequent changes to NECTOR (which is expected), you will
want to run `$ make run` to take care of everything for you.

    Note: The makefile will not activate or deactivate your virtualenv.
          If you plan on using one, you must do so manually.


---


## Misc. Notes

Let's try to stick with Python2 for now.

This is the main NECTOR project repo.

We'll be adding small applications to this project over time.

Applications:

- hosts (subnets)
- detection
- osint
- events
- reports


## Events

TODO: Add more to this section.

- An event is an observed change to the normal behavior of a system, environment, process, workflow or person. Examples: router ACLs were updated, firewall policy was pushed.
- An alert is a notification that a particular event (or series of events) has occurred, which is sent to responsible parties for the purpose of spawning action. Examples: the events above sent to on-call personnel.
- An incident is a human-caused, malicious event that leads to (or may lead to) a significant disruption of business. Examples: attacker posts company credentials online, attacker steals customer credit card database, worm spreading through network.*
