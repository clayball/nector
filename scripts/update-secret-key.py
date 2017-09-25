#!/usr/bin/env python2

'''
Purpose
=======

Generates a random Django-based secret key.


Postconditions
==============

Updates (or creates) a file named 'secretkey.txt' with the newly-generated key.
'''

import random

with open('secretkey.txt', 'w') as f:
    SECRET_KEY = ''.join([random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])
    f.write(SECRET_KEY)
    f.close()
