from __future__ import unicode_literals

from django.db import models
from django.shortcuts import get_object_or_404

from hosts.models import Host
from hosts.models import Subnet

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


    def get_host_id(self):
        """Returns the id of the Subnet that the Host belongs to."""
        try:
            ip = self.ipv4_address
            host = get_object_or_404(Host, ipv4_address=ip)
            host_id = host.id
            return host_id
        except:
            # I'm returning -1 so, rather than crash the server,
            # the user experiences a broken link. (Cludge)
            return '-1'


    def get_subnet_id(self):
        """Returns the id of the Subnet that the Host belongs to."""
        try:
            ip = self.ipv4_address
            ip_prefix = ip.rsplit('.', 1)[0]
            subnet = get_object_or_404(Subnet, ipv4_address__startswith=ip_prefix)
            subnet_id = subnet.id
            return subnet_id
        except:
            # I'm returning -1 so, rather than crash the server,
            # the user experiences a broken link. (Cludge)
            return '-1'


    host_id = property(get_host_id)
    subnet_id = property(get_subnet_id)
