from __future__ import unicode_literals

from django.db import models


# Create your models here.

class Event(models.Model):
    """Model for individual events, consisting of a request number,
    submission date, title, status, last edit date, submitters, and assignees."""
    request_number = models.CharField(max_length=10, default='')
    title = models.CharField(max_length=120, default='')
    date_submitted = models.CharField(max_length=12, default='')
    status = models.CharField(max_length=10, default='')
    date_last_edited = models.CharField(max_length=12)
    submitters = models.CharField(max_length=120)
    assignees = models.CharField(max_length=120)

    def __str__(self):
        return "%s, %s" % (self.request_number, self.title, self.date_submitted, self.status, self.date_last_edited, self.submitters, self.assignees)
