from __future__ import unicode_literals

from django.db import models


class ScanType(models.Model):
    """Model for types of nmap scans."""
    scan_name = models.CharField(default='My Custom Scan', max_length=255)

    # max_length = 19 in the event a range is used; 000.000.000.000-000
    host_address = models.CharField(default='0.0.0.0', max_length=19)

    ports = models.CharField(max_length=255)

    # String separated by comma
    scan_options = models.CharField(max_length=255)

    def __str__(self):
        return "%s, %s, %s" % (self.scan_name, self.host_address, self.ports)
