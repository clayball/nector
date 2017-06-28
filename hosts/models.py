from __future__ import unicode_literals
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User

from django.shortcuts import get_object_or_404

import json


class Host(models.Model):
    """Model for individual hosts, consisting of an ip and a hostname"""
    ipv4_address = models.GenericIPAddressField(protocol='ipv4', unique=True)
    host_name = models.CharField(max_length=80)
    os = models.CharField(max_length=50, default='')
    lsp = models.CharField(max_length=50, default='')
    location = models.CharField(max_length=25, default='')
    tags = models.CharField(max_length=50, default='')
    host_groups = models.CharField(max_length=125, default='')
    notes = models.CharField(max_length=320, default='')
    ports = models.TextField(default='')


    def __str__(self):
        return "%s, %s" % (self.ipv4_address, self.host_name)


    def get_number_open_ports(self):
        """Returns number of host's open ports."""
        # Host has no ports, return 0.
        if not self.ports:
            return 0

        # Host does have ports.
        else:
            # Convert the host's ports from a string to a JSON object.
            port_json = json.loads(self.ports)
            # Count number of ports current host has.
            port_count = 0
            for p in port_json:
                port_count += 1
            return port_count


    def get_clean_open_ports(self):
        """Returns list of clean open ports, ie no status, protocol, or date;
           just open port numbers."""
        open_ports = []
        if self.ports: # If the host has ports:
            port_json = json.loads(self.ports)
            has_open_port = False
            for p in port_json:
                # Port is open, add to list .
                if port_json[p][0] == 'open':
                    open_ports.append(str(p))
                    has_open_port = True
        return open_ports


    def get_clean_closed_ports(self):
        """Returns list of clean open ports, ie no status, protocol, or date;
           just open port numbers."""
        closed_ports = []
        if self.ports: # If the host has ports:
            port_json = json.loads(self.ports)
            has_closed_port = False
            for p in port_json:
                # Port is open, add to list .
                if port_json[p][0] == 'closed':
                    closed_ports.append(str(p))
                    has_closed_port = True
        return closed_ports


    def get_subnet_id(self):
        """Returns the id of the Subnet that the Host belongs to."""
        ip = self.ipv4_address
        ip_prefix = ip.rsplit('.', 1)[0]
        subnet = get_object_or_404(Subnet, ipv4_address__startswith=ip_prefix)
        subnet_id = subnet.id
        return subnet_id


    num_open_ports = property(get_number_open_ports)
    open_ports = property(get_clean_open_ports)
    closed_ports = property(get_clean_closed_ports)
    subnet_id = property(get_subnet_id)


    class Meta:
        permissions = (
            ("edit_host", "Can edit host information"),
        )


class Subnet(models.Model):
    """Model for subnets, consisting of an ip address and a suffix"""
    ipv4_address = models.GenericIPAddressField(protocol='ipv4', default='0.0.0', unique=True)
    suffix = models.CharField(max_length=2, default='.x')

    def __str__(self):
        return "%s%s" % (self.ipv4_address, self.suffix)


class HostVisits(models.Model):
    user = models.ForeignKey(User, default=0)
    ipv4_address = models.GenericIPAddressField(protocol='ipv4')
    visits = models.IntegerField(default=0)

    def __str__(self):
        return "%s, %s, %s" % (self.user, self.ipv4_address, self.visits)
