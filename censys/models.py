from __future__ import unicode_literals

from django.db import models

class Account(models.Model):
    """
     Model for user's Censys account, consisting
     of an API key and a SECRET key.
    """
    api_key = models.CharField(max_length=80, unique=True)
    secret = models.CharField(max_length=80)

    def __str__(self):
        return "%s, %s" % (self.api_key, self.secret)
