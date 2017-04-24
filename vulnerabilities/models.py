from __future__ import unicode_literals

from django.db import models


# Create your models here.

class Vulnerability(models.Model):
    """Model for individual vulnerabilities, consisting of a plugin ID,
    plugin name, severity of vulnerability, ipv4 address of affected host, & host name of affected host."""
    plugin_and_host = models.CharField(max_length=90, default='', unique=True)
    plugin_id = models.CharField(max_length=10, default='')
    plugin_name = models.CharField(max_length=120, default='')
    severity = models.CharField(max_length=10, default='')
    ipv4_address = models.GenericIPAddressField(protocol='ipv4', default='0.0.0.0')
    host_name = models.CharField(max_length=80)


    def __str__(self):
        return "%s, %s" % (self.plugin_and_host, self.plugin_id, self.plugin_name, self.severity, self.ipv4_address, self.host_name)
