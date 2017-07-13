from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

class ScanType(models.Model):
    """Model for types of nmap scans."""

    user = models.ForeignKey(User, default=0)

    scan_name = models.CharField(max_length=255, unique=True)

    # max_length = 19 in the event a range is used; 000.000.000.000-000
    host_address = models.CharField(max_length=19)

    ports = models.CharField(max_length=255)

    # String separated by comma
    scan_options = models.CharField(max_length=255)

    def __str__(self):
        return "%s, %s, %s, %s" % (self.scan_name, self.user, self.host_address, self.ports)
