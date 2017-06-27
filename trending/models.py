from __future__ import unicode_literals

from django.db import models


class RSSFeed(models.Model):
    """Model for RSS Feeds."""
    url = models.CharField(max_length=255, default='')

    def __str__(self):
        return "%s" % (self.url)
