from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


class RSSFeed(models.Model):
    """Model for RSS Feeds."""
    user = models.ForeignKey(User, default=0)
    url = models.CharField(max_length=255, default='')

    def __str__(self):
        return "%s" % (self.url)
