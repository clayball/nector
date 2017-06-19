from __future__ import unicode_literals
from datetime import datetime

from django.db import models


class Host(models.Model):
    """Model for individual hosts, consisting of an ip and a hostname"""
    ipv4_address = models.GenericIPAddressField(protocol='ipv4', default='0.0.0.0', unique=True)
    host_name = models.CharField(max_length=80)
    os = models.CharField(max_length=50, default='')
    lsp = models.CharField(max_length=50, default='')
    location = models.CharField(max_length=25, default='')
    tags = models.CharField(max_length=50, default='')
    host_groups = models.CharField(max_length=125, default='')
    notes = models.CharField(max_length=320, default='')
    ports = models.TextField(default='')
    status = models.CharField(max_length=120, default='')

    def __str__(self):
        return "%s, %s" % (self.ipv4_address, self.host_name)


class Subnet(models.Model):
    """Model for subnets, consisting of an ip address and a network prefix"""
    ipv4_address = models.GenericIPAddressField(protocol='ipv4', default='0.0.0.0', unique=True)
    prefix = models.IntegerField()

    def __str__(self):
        return "%s/%s" % (self.ipv4_address, self.prefix)
