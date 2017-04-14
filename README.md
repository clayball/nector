# NECTOR - by haXor2 for haX0rs

![nector home](nector-home.png)

Lets try to stick with Python2 for now.

This is the main NECTOR project repo.

We'll be adding small applications to this project over time.

Applications:

- hosts (in progress)
- scans (in progress)
- ipranges (todo)
- ossec alerts (todo)

Getting Started
---------------

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

I created a superuser account for by doing the following.

```
$ python manage.py createsuperuser --username=clayw --email=clayw@sas.upenn.edu
```

Login by going to 127.0.0.1:8000/admin

