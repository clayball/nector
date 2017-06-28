from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader
import django_tables2 as tables
from django_tables2 import RequestConfig

from .models import Vulnerability
from hosts.models import Host
from hosts.models import Subnet

class VulnTable(tables.Table):
    plugin_id = tables.Column(verbose_name='Plugin ID',
                              attrs={'th' : {'class' : 'td-content'},
                                     'td' : {'class' : 'td-content'}})

    plugin_name = tables.Column(verbose_name='Plugin Name',
                                attrs={'th' : {'class' : 'td-content'},
                                       'td' : {'class' : 'td-content'}})
    severity = tables.Column(verbose_name='Severity',
                                attrs={'th' : {'class' : 'td-content'},
                                       'td' : {'class' : 'td-content'}})

    ipv4_address = tables.TemplateColumn('<a href="/hosts/search/?input_ip={{record.ipv4_address}}">{{record.ipv4_address}}</a>',
                                        verbose_name='IPv4 Address',
                                        attrs={'th' : {'class' : 'td-content'},
                                               'td' : {'class' : 'td-content'}})

    host_name = tables.TemplateColumn('<a href="/hosts/search/?input_ip={{record.host_name}}">{{record.host_name}}</a>',
                                      verbose_name='Host Name',
                                      attrs={'th' : {'class' : 'td-content'},
                                             'td' : {'class' : 'td-content'}})

    class Meta:
        td_attrs = {
            'class': 'td-content'
        }



def index(request):
    '''Renders page containing all vulnerabilities in the database.'''

    # Retrieve all vulnerabilities in db.
    vuln_list = Vulnerability.objects.all()

    # Set up table to display Vulnerabilities.
    vuln_table = VulnTable(vuln_list)
    RequestConfig(request, paginate={'per_page':100}).configure(vuln_table)

    # Pass context to rendered page.
    context = {'vuln_list' : vuln_list,
               'vuln_table' : vuln_table}

    return render(request, 'vulnerabilities/vulnz.html', context)
