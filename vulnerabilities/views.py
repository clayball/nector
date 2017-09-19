from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.template.context_processors import csrf
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

    ipv4_address = tables.TemplateColumn('<a href="/hosts/{{record.subnet_id}}/host/{{record.host_id}}">{{record.ipv4_address}}</a>',
                                        verbose_name='IPv4 Address',
                                        attrs={'th' : {'class' : 'td-content'},
                                               'td' : {'class' : 'td-content'}})

    host_name = tables.TemplateColumn('<a href="/hosts/{{record.subnet_id}}/host/{{record.host_id}}">{{record.host_name}}</a>',
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
    vuln_table = VulnTable(list(vuln_list))
    RequestConfig(request, paginate={'per_page':100}).configure(vuln_table)

    # Pass context to rendered page.
    context = {'vuln_list' : vuln_list,
               'vuln_table' : vuln_table}

    return render(request, 'vulnerabilities/vulnz.html', context)


def search(request):
    '''Renders page containing queried malware.'''
    context = {}

    context['user'] = request.user
    context['request'] = request

    if request.method == "POST":

        form = request.POST
        context.update(csrf(request))

        context['user'] = request.user

        context['request'] = request

        vulnz_keywords = request.POST['vulnz_keywords']

        vulnz_list = Vulnerability.objects.all()

        # Check if multiple ports entered (ex 80, 443)
        if ',' in vulnz_keywords:
            words = vulnz_keywords.split(',')
            # Filter each specified keyword, one at a time.
            for w in words:
                w = w.strip()
                vulnz_list_temp = vulnz_list.filter(plugin_id__icontains=w)
                vulnz_list_temp = vulnz_list_temp | \
                                    vulnz_list.filter(plugin_name__icontains=w)
                vulnz_list_temp = vulnz_list_temp | \
                                    vulnz_list.filter(severity__icontains=w)
                vulnz_list_temp = vulnz_list_temp | \
                                    vulnz_list.filter(ipv4_address__icontains=w)
                vulnz_list_temp = vulnz_list_temp | \
                                    vulnz_list.filter(host_name__icontains=w)
                vulnz_list = vulnz_list_temp
        elif vulnz_keywords.strip():
            w = vulnz_keywords.strip()
            # Single keyword entered, so single filter needed:
            vulnz_list_temp = vulnz_list.filter(plugin_id__icontains=w)
            vulnz_list_temp = vulnz_list_temp | \
                                vulnz_list.filter(plugin_name__icontains=w)
            vulnz_list_temp = vulnz_list_temp | \
                                vulnz_list.filter(severity__icontains=w)
            vulnz_list_temp = vulnz_list_temp | \
                                vulnz_list.filter(ipv4_address__icontains=w)
            vulnz_list_temp = vulnz_list_temp | \
                                vulnz_list.filter(host_name__icontains=w)
            vulnz_list = vulnz_list_temp


        # Set up table to display Malware.
        vuln_table = VulnTable(list(vulnz_list))
        RequestConfig(request, paginate={'per_page':100}).configure(vuln_table)

        # Pass context to rendered page.
        context['vuln_list'] = vulnz_list
        context['vuln_table'] = vuln_table

        # We're not exporting, so render the page with a table.
        return render(request, 'vulnerabilities/vulnz.html', context)

    context.update(csrf(request))
    return render(request, 'vulnerabilities/vulnz.html', context)
