from django.shortcuts import render, get_object_or_404
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import loader
from django.template.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.utils.html import escape

import django_tables2 as tables
from django_tables2 import RequestConfig

from .models import Host
from .models import Subnet
from .models import Alert
from .models import HostVisits
from django.db import models
from vulnerabilities.models import Vulnerability
from forms import HostForm
from forms import SearchForm

import json
import copy

import subprocess # For ping

from selenium import webdriver # For screenshotting host website.
from selenium.common.exceptions import WebDriverException # For errors

# Exporting CSV
import csv
from django.http import StreamingHttpResponse


class HostsTable(tables.Table):

    ipv4_address = tables.TemplateColumn('<a href="/hosts/{{record.subnet_id}}/host/{{record.id}}">{{record.ipv4_address}}</a>',
                                        verbose_name='IPv4 Address',
                                        attrs={'th' : {'class' : 'td-content'},
                                               'td' : {'class' : 'td-content'}})

    host_name = tables.TemplateColumn('<a href="/hosts/{{record.subnet_id}}/host/{{record.id}}">{{record.host_name}}</a>',
                                      verbose_name='Host Name',
                                      attrs={'th' : {'class' : 'td-content'},
                                             'td' : {'class' : 'td-content'}})

    num_open_ports = tables.Column(verbose_name='No. Open Ports',
                                attrs={'th' : {'class' : 'td-content'},
                                       'td' : {'class' : 'td-content'}})
    # Meta class used for built-in attribute modification.
    class Meta:
        td_attrs = {
            'class': 'td-content'
        }


class AlertTable(tables.Table):

    ipv4_address = tables.TemplateColumn('<a href="/hosts/{{record.host.subnet_id}}/host/{{record.host.id}}">{{record.ipv4_address}}</a>',
                                        verbose_name='IPv4 Address',
                                        attrs={'th' : {'class' : 'td-content'},
                                               'td' : {'class' : 'td-content'}})

    host_name = tables.TemplateColumn('<a href="/hosts/{{record.host.subnet_id}}/host/{{record.host.id}}">{{record.host.host_name}}</a>',
                                      verbose_name='Host Name',
                                      attrs={'th' : {'class' : 'td-content'},
                                             'td' : {'class' : 'td-content'}})

    message = tables.Column(verbose_name='Alert Message',
                                attrs={'th' : {'class' : 'td-content'},
                                       'td' : {'class' : 'td-content'}})

    date = tables.Column(verbose_name='Date',
                                attrs={'th' : {'class' : 'td-content'},
                                       'td' : {'class' : 'td-content'}})

    # Meta class used for built-in attribute modification.
    class Meta:
        td_attrs = {
            'class': 'td-content'
        }




def index(request):
    '''Renders hosts/index.html, displaying list of subnets.'''

    context = {}

    # Get all the subnet objects.
    subnet_list = Subnet.objects.all()

    # Use this list to store subnets without their masks (aka the .0/24 piece)
    # as strings in a list.
    # We're doing this for ease of sorting.
    ipv4_list = []
    for subnet in subnet_list:
        ipv4_list.append(subnet.ipv4_address)

    # Sort the maskless subnets.
    sorted_subnet_list = sort_ip_list(ipv4_list)

    # Get sorted Subnet objects using sorted subnet strings.
    # (Aka "convert" list to QuerySet)
    sorted_subnet_qset = []
    for s in sorted_subnet_list:
        sorted_subnet_qset.append(Subnet.objects.get(ipv4_address=s))

    # Gets subnets as 10.0 (aka 10.0.x.x) for ease of view in index template.
    sorted_narrowed_subnet_list = set()
    for s in sorted_subnet_list:
        narrowed_subnet = s.rsplit('.', 1)[0]
        sorted_narrowed_subnet_list.add(narrowed_subnet)

    # narrowed_subnet_dict['10.0'] returns '[SubnetA, SubnetB, ...]'
    narrowed_subnet_dict = {}
    for n in sorted_narrowed_subnet_list:
        narrowed_subnet_dict[n] = []
        for s in sorted_subnet_qset:
            if n in s.ipv4_address:
                narrowed_subnet_dict[n].append(s)


    # Get frequently visited hosts.
    if request.user.is_authenticated():
        frequent_host_visits_list = (HostVisits.objects
                                        .filter(user=request.user)
                                        .order_by('-visits')[:10])
        frequent_host_list = []
        for h in frequent_host_visits_list:
            host_obj = Host.objects.get(ipv4_address=h.ipv4_address)
            frequent_host_list.append(host_obj)
        context['frequent_host_list'] = frequent_host_list


    # Get newest alerts.
    newest_alerts_list = Alert.objects.all().order_by('-id')[:25]
    context['newest_alerts_list'] = newest_alerts_list


    # Context to pass to hosts/index.html so we can use its key,value pairs as
    # variables in the template.
    context['subnet_list'] = sorted_subnet_qset
    context['narrowed_subnet_list'] = sorted_narrowed_subnet_list
    context['narrowed_subnet_dict'] = narrowed_subnet_dict

    return render(request, 'hosts/index.html', context)


def detail(request, subnet_id):
    '''Display hosts residing on selected subnet.'''

    context = {}

    if request.method == 'GET':
        if 'select_hosts' in request.GET:

            # Get value of dropdown menu ('named','unnamed','all')
            limit_type = request.GET['select_hosts']

            # Get Subnet object of current subnet page.
            # Use Subnet object to get the maskless IP addr
            # for obtaining the subnet's hosts.
            subnet = get_object_or_404(Subnet, pk=subnet_id)
            address = subnet.ipv4_address

            host_list = []
            # Get queryset of (unsorted) hosts that belong to our subnet.
            if limit_type == 'named':
                host_list = Host.objects.filter(ipv4_address__startswith=address)
                host_list = host_list.exclude(host_name='NXDOMAIN')
            elif limit_type == 'unnamed':
                host_list = Host.objects.filter(ipv4_address__startswith=address)
                host_list = host_list.filter(host_name='NXDOMAIN')
            else:
                host_list = Host.objects.filter(ipv4_address__startswith=address)

            # Pass queryset of hosts to helper function
            # so we can pull out each host's IP addr.
            unsorted_host_list = get_ip_list(host_list)

            # Pass unsorted host list to helper function that
            # returns a list of sorted IP addrs.
            sorted_host_list = sort_ip_list(unsorted_host_list)

            # Will contain a queryset
            # of Host objs sorted by
            # their IPv4 addrs.
            sorted_host_set = []

            # Iterate through sorted host
            # list to add each host to our
            # queryset 'sorted_host_set'.
            for h in sorted_host_list:
                sorted_host_set.append(Host.objects.get(ipv4_address=h))

            # Set up table to display Hosts.
            hosts_table = HostsTable(list(host_list))
            RequestConfig(request, paginate={'per_page':256}).configure(hosts_table)
            # Add to context.
            context['host_list'] = sorted_host_set
            context['limit'] = limit_type
            context['subnet'] = subnet
            context['subnet_id'] = subnet_id
            context['hosts_table'] = hosts_table

        else:

            limit_type = request.GET.get('select_hosts')

            # Get Subnet object that was selected.
            subnet = get_object_or_404(Subnet, pk=subnet_id)

            # Break up the subnet address so we can get hosts that fall under its
            # subnet.
            address = subnet.ipv4_address

            # Get hosts that start with the same address as the subnet.
            host_list = Host.objects.filter(ipv4_address__startswith=address)

            # Set up table to display Hosts.
            hosts_table = HostsTable(list(host_list))
            RequestConfig(request, paginate={'per_page':256}).configure(hosts_table)

            # Context to pass to hosts/index.html so we can use its key,value pairs as
            # variables in the template.
            context = {'host_list': host_list, 'subnet_id' : subnet_id,
                       'subnet' : subnet, 'limit' : limit_type, 'hosts_table' : hosts_table}
    return render(request, 'hosts/detail.html', context)


def detail_host(request, subnet_id, host_id, ping_status='', screenshot_path=''):
    '''Display selected host information.'''

    # Check if we are just pinging the host.
    if request.POST.get("host_to_ping") and ping_status == '':
        return ping(request, subnet_id, host_id)

    # Check if we are just getting a screenshot of the host.
    if request.POST.get("host_to_screenshot") and screenshot_path == '':
        return screenshot_host(request, subnet_id, host_id)

    # Get selected Host object.
    host = get_object_or_404(Host, pk=host_id)

    # Add page count +1 for user.
    if request.user.is_authenticated():
        ipv4_address = host.ipv4_address
        user = request.user
        # Check if HostVisit is already in database.
        if HostVisits.objects.filter(ipv4_address=ipv4_address, user=user).exists():
            # If it is, then add 1 to its number of visits.
            host_visit = get_object_or_404(HostVisits, ipv4_address=ipv4_address, user=user)
            host_visit.visits += 1
            try:
                host_visit.save()
            except Exception as e:
                print '[!] %s' % e
        else:
            # HostVisit doesn't exist in our db, so create a new one.
            host_visit = HostVisits(ipv4_address=ipv4_address, user=user, visits=1)
            # Save HostVisit to db
            try:
                host_visit.save()
            # Error, don't save and warn the user.
            except Exception as e:
                print '[!] %s' % e

    # Save current host to session.
    # This will be used to see what host the user last visited.
    # Its purpose is to ensure the user is editing the right host,
    # if he/she chooses to do so.
    request.session['last-host'] = host.ipv4_address

    # Get vulnerabilities of selected Host.
    vuln_list = Vulnerability.objects.filter(ipv4_address=host.ipv4_address)

    # Ports are stored in our db as a string following json formatting,
    # ie. { 'port' : ['state', 'protocol', 'date'] }
    # ex. { '80' : ['open', 'Apache2', '150509']}
    port_list = []
    port_status_list = []
    port_info_list = []
    port_date_list = []

    # Does the host have any ports?
    if host.ports:
        # Convert the host's ports from a string to a JSON object.
        port_json = json.loads(host.ports)

        # Get the number, state, protocol, and date of each port in our
        # JSON object.
        for p in port_json:
            port_list.append(p)
            port_status_list.append(port_json[p][0])
            port_info_list.append(port_json[p][1])
            port_date_list.append(port_json[p][2])

        # Pass context containing port information.
        context = {'host': host, 'subnet_id' : subnet_id, 'ping_status' : ping_status,
                   'vuln_list' : vuln_list, 'port_data' : zip(port_list,
                                                              port_status_list,
                                                              port_info_list,
                                                              port_date_list),
                   'screenshot_path' : screenshot_path,
                  }

    else:
        # Pass context with no port information (bc host has no ports).
        context = {'host': host, 'subnet_id' : subnet_id, 'ping_status' : ping_status,
                   'vuln_list' : vuln_list, 'port_data' : None, 'screenshot_path' : screenshot_path}

    return render(request, 'hosts/detail_host.html', context)


def ping(request, subnet_id, host_id):

    if 'host_to_ping' not in request.POST:
        if 'next' in request.POST:
            return HttpResponseRedirect(request.POST['next'])

    ip = request.POST['host_to_ping']
    status = subprocess.call(['ping', '-c1', '-w2', ip])

    str_status = ''
    if status == 0:
        str_status = 'Online'
    else:
        str_status = 'Offline'

    return detail_host(request, subnet_id, host_id, str_status)


@login_required
# @permission_required permissions are being saved to host model -> Meta
# consider making a separate permission for each lsp
#@permission_required('hosts.edit_host', raise_exception=True)
def edit(request):
    '''Edit a host's information.'''
    # The request method used (GET, POST, etc) determines what dict 'context'
    # gets filled with.
    context = {}

    # If we have a non-empty POST request, that means
    # the user is submitting / loading the form.
    if request.POST:

        # 'update_form' is a hidden tag in our template's form.
        # If it exists in our POST, then the user is submitting the form.
        # Otherwise, the user is loading the form.
        if 'update_form' not in request.POST:
            host_ip = request.session['last-host']
            host = get_object_or_404(Host, ipv4_address=host_ip)
            context['host'] = host
            form = HostForm(instance=host)
        else:
            # Retrieve IP addr user entered into form.
            # Use that IP to get respective Host object.
            host_ip = request.session['last-host']
            host = get_object_or_404(Host, ipv4_address=host_ip)

            # Load form with provided information so we can save the form as
            # an object. (See forms.py and docs on ModelForms for more info)
            form = HostForm(request.POST, instance=host)

            # form.is_valid() checks that updated instance object's new attributes
            # are valid. Calling form.save() will actually save them to the db.
            if form.is_valid():

                # Save attributes from form into those of a Host object.
                form.save()

                # Get ip addr of updated Host so we can direct user to its page
                # after editing.
                new_ip = request.session['last-host']

                return HttpResponseRedirect('/hosts/search/?input_ip=%s' % new_ip)

    # Request method was empty, so user wants to create new Host.
    # Create empty form.
    else:
        if 'last-host' in request.session:
            host_ip = request.session['last-host']
            host = get_object_or_404(Host, ipv4_address=host_ip)
            context['host'] = host
            form = HostForm(instance=host)
        else:
            form = HostForm()

    # Add new CSRF token and form to context.
    context.update(csrf(request))
    context['form'] = form
    return render(request, 'hosts/edit_host.html', context)


def alerts(request):
    context = {}
    alert_list = Alert.objects.all().order_by('-id')

    # Set up table to display Alerts.
    alert_table = AlertTable(list(alert_list))
    RequestConfig(request, paginate={'per_page':100}).configure(alert_table)

    context['alert_table'] = alert_table
    context['alert_list'] = alert_list

    return render(request, 'hosts/alerts.html', context)


def ports(request):

    context = {}

    context['user'] = request.user
    context['request'] = request

    if request.method == "POST":

        form = request.POST
        context.update(csrf(request))

        port_numbers  = ''
        port_services = ''
        port_dates    = ''

        context['request'] = request
        context['user'] = request.user

        if 'port_nums' in request.POST:
            port_numbers = request.POST['port_nums'].strip()

        if 'port_servs' in request.POST:
            port_services = request.POST['port_servs'].strip()

        if 'port_dates' in request.POST:
            port_dates = request.POST['port_dates'].strip()

        host_list = {}

        # Check if multiple ports entered (ex 80, 443)
        if ',' in port_numbers:
            ports = port_numbers.split(',')
            # Filter each specified port, one at a time.
            host_list = Host.objects.all()
            for p in ports:
                p = p.strip()
                host_list = host_list.filter(ports__icontains='"'+p+'"')
        elif port_numbers.strip():
            # Single port entered, so single filter needed:
            host_list = Host.objects.filter(ports__icontains='"'+port_numbers+'"')

        if port_services:
            # Multiple words entered, so check each word leniently.
            # (ie, break apart each word and check for each in the ports field)
            if ' ' in port_services:
                port_services = port_services.split(" ")
                for s in port_services:
                    if not host_list:
                        host_list = Host.objects.filter(ports__icontains=s)
                    else:
                        host_list = host_list.filter(ports__icontains=s)

        if port_dates:
            if not host_list:
                host_list = Host.objects.filter(ports__icontains=port_dates)
            else:
                host_list = host_list.filter(ports__icontains=port_dates)


        for h in host_list:
            if h.ports: # If the host has ports:
                port_json = json.loads(h.ports)
                h_ports = []
                for p in port_json:
                    # Port is closed, remove Host from host_list.
                    if p == port_numbers:
                        if port_json[p][0] == 'closed':
                            host_list = host_list.exclude(ipv4_address=h.ipv4_address)


        context['host_list'] = host_list

        # We're not exporting, so render the page with a table.
        return render_to_response('hosts/ports.html', context)

    context.update(csrf(request))
    return render_to_response('hosts/ports.html', context)


def ports_to_json_format(ports, states, protos, dates):
    '''Takes lists of CSVs and stores them all into a single dictionary
       following JSON formatting. Returns the dictionary.'''

    # Return value.
    dict_ports = {}

    # Break up our CSV lists so we can get the info we need.
    # Each index corresponds with a particular port,
    # ie states[0], protos[0], dates[0] all correspond to ports[0].
    #    states[1], protos[1], dates[1] all correspond to ports[1].
    ports  = ports.split(',')
    states = states.split(',')
    protos = protos.split(',')
    dates  = dates.split(',')

    # Make sure lists are all the same length.
    # Necessary for below for-loop.
    max_len = max(len(ports), len(states), len(protos), len(dates))
    while len(ports) != max_len:
        ports.append('')
    while len(states) != max_len:
        states.append('')
    while len(protos) != max_len:
        protos.append('')
    while len(dates) != max_len:
        dates.append('')

    # Zip the data together so we can iterate while keeping
    # corresponding indices.
    port_data = zip(ports, states, protos, dates)

    # Iterate through all Port Information so we store
    # each Port + Port details into our return value dict.
    for port, state, proto, date in port_data:

        # Remove whitespace
        # from each element.
        port  = port.strip()
        state = state.strip()
        proto = proto.strip()
        date  = date.strip()

        # If dict_ports has any data (aka loop is not
        # on its first iteration), then load it as a
        # temp JSON dictionary. We can manipulate the
        # JSON a lot easier.
        # Store state, proto, and date into respective
        # port key of dictionary.
        tmp_dict_ports = {}
        if dict_ports:
            tmp_dict_ports = json.loads(dict_ports)
        tmp_dict_ports[port] = [state, proto, date]

        # Dump our temp dict from JSON into string.
        dict_ports = json.dumps(tmp_dict_ports)

    return dict_ports


def get_ip_list(queryset):
    '''Returns list of extracted IPv4
       addresses from a QuerySet of
       Host objects. Acts as helper
       function to limit_hosts()'''

    # Return value of unsorted IPv4 addrs.
    unsorted_host_list = []

    # Iterate through Hosts in QuerySet.
    for h in queryset:
        # Get IP from host and add IP
        # to our return value list.
        ip = str(h).split(',', 1)[0]
        unsorted_host_list.append(ip)

    return unsorted_host_list


def sort_ip_list(unsorted_host_list):
    '''Returns sorted list of IP addresses.
       Acts as helper function to limit_hosts().'''
    return sorted(unsorted_host_list,
                  key=lambda ip: long(''.join(["%02X" % long(i) \
                  for i in ip.split('.')]), 16))


def search_host(request):
    '''Renders page of Host specified in Search Box.'''

    try:
        if request.method == 'GET':

            context = {}

            # Get data entered in Search Box.
            dirty_query = request.GET.get('input_ip', None).strip()

            # Sanitize query.
            query = escape(dirty_query)

            # --
            # Render Host or Subnet page if we can deduce what was entered.
            # --

            # Check if existing IPv4 Address.
            if Host.objects.filter(ipv4_address=query).exists():
                # Get corresponding id(s) for queried IP.
                # Should only return 1 id.
                host_id_list = Host.objects.filter(ipv4_address=query)\
                                              .values_list('id', flat=True)

                # Get host object based on obtained id.
                host = get_object_or_404(Host, pk=host_id_list[0])
                host_id = host.id

                # Get subnet object based on host.
                host_prefix = host.ipv4_address.rsplit('.', 1)[0]
                subnet = get_object_or_404(Subnet, ipv4_address__startswith=host_prefix)
                subnet_id = subnet.id

                return detail_host(request, subnet_id, host_id)


            # Check if existing Host Name.
            if Host.objects.filter(host_name=query).exists():
                # Get corresponding id(s) for queried IP.
                # Should only return 1 id.
                host_id_list = Host.objects.filter(host_name=query)\
                                              .values_list('id', flat=True)

                # Get host object based on obtained id.
                host = get_object_or_404(Host, pk=host_id_list[0])
                host_id = host.id

                # Get subnet object based on host.
                host_prefix = host.ipv4_address.rsplit('.', 1)[0]
                subnet = get_object_or_404(Subnet, ipv4_address__startswith=host_prefix)
                subnet_id = subnet.id

                return detail_host(request, subnet_id, host_id)


            # Check if existing Subnet inputed as 0.0.0
            if Subnet.objects.filter(ipv4_address=query).exists():
                subnet = get_object_or_404(Subnet, ipv4_address=query)
                subnet_id = subnet.id
                return detail(request, subnet_id)


            # Check if existing Subnet inputted as 0.0.0.x
            try:
                possible_subnet = query.rsplit('.', 1)[0]
                if Subnet.objects.filter(ipv4_address=possible_subnet).exists():
                    subnet = get_object_or_404(Subnet, ipv4_address=possible_subnet)
                    subnet_id = subnet.id
                    return detail(request, subnet_id)
            except:
                pass


            # --
            # Display table of Hosts related to query.
            # --

            host_list = Host.objects.filter(host_name__icontains=query)

            print host_list

            if host_list:
                # Set up table to display Hosts.
                hosts_table = HostsTable(list(host_list))
                RequestConfig(request, paginate={'per_page':256}).configure(hosts_table)
                # Add to context.
                context['host_list'] = host_list
                context['hosts_table'] = hosts_table

                ## Inputted query not found in our db, so load page with no host.
                return render(request, 'hosts/search_results.html', context)
            else:
                ## Inputted query not found in our db, so load page with no host.
                return render(request, 'hosts/detail_host.html')

    except:
        ## Inputted query not found in our db, so load page with no host.
        print 'ERR (hosts/views.py -> search_hosts())'
        return render(request, 'hosts/detail_host.html')


def is_subnet(query):
    '''Returns True if
       query is valid
       subnet. Otherwise,
       returns False.
       Acts as helper
       function to
       search_host()'''

    if '/' in query:
        mask_split = query.split('/')
        bits = mask_split[0].split('.')
        if len(bits) != 4: return False
        try: return all(0<=int(p)<256 for p in bits)
        except ValueError: return False
    return False


def is_ip(query):
    '''Returns True if
       query is valid
       IPv4. Otherwise,
       returns False.
       Acts as helper
       function to
       search_host()'''

    pieces = query.split('.')
    if len(pieces) != 4: return False
    try: return all(0<=int(p)<256 for p in pieces)
    except ValueError: return False


def search(request):
    '''
    Default search page.
    If a POST request was made to get here, then our form was submitted,
    so display a table of the query made.
    Otherwise, just display the form.
    '''

    exporting = False

    if request.POST.get("export"):
        # User pressed Export button.
        exporting = True

    if request.method == "POST":
        # User is either Generating a table to the page (exporting=False)
        #             or Exporting to a CSV file (exporting=True).

        # Get form information.
        form = SearchForm(request.POST)

        if form.is_valid():

            # Append important info to context.
            context = {}
            context['checks'] = request.POST.getlist('checks')
            context['rad'] = request.POST.getlist('rad')
            processed_query = process_query(form, context['checks'], context['rad'])
            context['open_ports'], context['host_list'] = get_open_ports_and_new_list(processed_query)
            context['subnet_list'] = get_subnet_list(context['host_list'])
            context['host_data'] = zip(context['host_list'], context['subnet_list'])
            context.update(csrf(request))
            context['form'] = form

            # If we're exporting, export!
            if exporting:
                return export(request, context)

            # We're not exporting, so render the page with a table.
            return render(request, 'hosts/search.html', context)

    context = {}
    context.update(csrf(request))
    context['form'] = SearchForm()
    context['checks'] = ['ipv4_address', 'host_name', 'ports']
    return render(request, 'hosts/search.html', context)


def process_query(form, checks, rad):
    '''
    Parses data from form and gets all objects that have that data.
    Returns QuerySet of Hosts.
    '''
    ipv4_address = form.cleaned_data['ipv4_address']
    host_name = form.cleaned_data['host_name']
    ports = form.cleaned_data['ports']
    os = form.cleaned_data['os']
    lsp = form.cleaned_data['lsp']
    host_groups = form.cleaned_data['host_groups']
    location = form.cleaned_data['location']
    tags = form.cleaned_data['tags']
    notes = form.cleaned_data['notes']
    service = form.cleaned_data['services']

    host_list = []



    # Check if multiple ports entered (ex 80, 443)
    if ',' in ports:
        ports = ports.split(',')
        host_list = Host.objects.filter(ipv4_address__icontains=ipv4_address,
                                        host_name__icontains=host_name,
                                        os__icontains=os,
                                        lsp__icontains=lsp,
                                        host_groups__icontains=host_groups,
                                        location__icontains=location,
                                        tags__icontains=tags,
                                        notes__icontains=notes)
        # Filter each specified port, one at a time.
        for p in ports:
            p = p.strip()
            host_list = host_list.filter(ports__icontains='"'+p+'"')
    elif ports.strip():
        # Single port entered, so single filter needed:
        host_list = Host.objects.filter(ipv4_address__icontains=ipv4_address,
                                        host_name__icontains=host_name,
                                        ports__icontains='"'+ports+'"',
                                        os__icontains=os,
                                        lsp__icontains=lsp,
                                        host_groups__icontains=host_groups,
                                        location__icontains=location,
                                        tags__icontains=tags,
                                        notes__icontains=notes)
    else:
        # No port entered:
        host_list = Host.objects.filter(ipv4_address__icontains=ipv4_address,
                                        host_name__icontains=host_name,
                                        os__icontains=os,
                                        lsp__icontains=lsp,
                                        host_groups__icontains=host_groups,
                                        location__icontains=location,
                                        tags__icontains=tags,
                                        notes__icontains=notes)
    if service:
        # Multiple words entered, so check each word leniently.
        # (ie, break apart each word and check for each in the ports field)
        if ' ' in service:
            service_list = service.split(" ")
            for s in service_list:
                if not host_list:
                    host_list = Host.objects.filter(ports__icontains=s)
                else:
                    host_list = host_list.filter(ports__icontains=s)
        else:
            host_list = host_list.filter(ports__icontains=service)

    '''
    # Did we select Online-Only or Offline-Only or All Hosts?
    if 'online' in rad:
        host_list = host_list.exclude(status__icontains='Offline')
    elif 'offline' in rad:
        host_list = host_list.filter(status__icontains='Offline')
    '''

    return host_list


def get_open_ports_and_new_list(host_list):
    '''
    Returns a tuple following (open_ports, host_list).
    open_ports is a dict following {ip: [ports]}.
    host_list is a QuerySet.
    Example return value:
        {'123.45.67.89': ['80', '443']}, <Host QuerySet>
    If a port is not open, then we won't add the port to the dict.
    If a port is not open, then we will remove the respective Host
    from the host_list since we don't want to display that Host.
    '''
    open_ports = {}
    for h in host_list:
        if h.ports: # If the host has ports:
            port_json = json.loads(h.ports)
            h_ports = []
            has_open_port = False
            for p in port_json:
                # Port is open, add to list .
                if port_json[p][0] == 'open':
                    h_ports.append(str(p))
                    has_open_port = True
                # Port is closed, remove Host from host_list.
                elif port_json[p][0] == 'closed':
                    host_list = host_list.exclude(ipv4_address=h.ipv4_address)
                else:
                    print 'Something went wrong! (hosts/views.py -> get_open_ports_and_new_list())'
            # Make sure it has an open port before we add it to the final dict.
            # Otherwise, we are throwing in an empty list, and who needs that?
            if has_open_port:
                open_ports[str(h.ipv4_address)] = h_ports
    return open_ports, host_list


def get_subnet_list(host_list):
    subnet_list = []
    for h in host_list:
        h_ip = h.ipv4_address
        subnet_address = h_ip.rsplit('.', 1)
        try:
            subnet_list.append(Subnet.objects.get(ipv4_address__startswith=subnet_address[0]))
        except:
            print 'ERROR: Could not find subnet for ' + h_ip
    return subnet_list


class Echo(object):
    '''
    An object that implements just the write method of the file-like
    interface.
    '''
    def write(self, value):
        '''Write the value by returning it, instead of storing in a buffer.'''
        return value

def export(request, context):
    '''
    Looks at what info the user wants exported, and parses that out of
    'context'.
    Returns a response that creates a popup on the page asking the user
    to download a CSV file.
    Uses the Echo class (above) as a means of storing data in a buffer.
    '''

    existing_header_columns = []

    # Bools to keep track of what was selected.
    # Will be used for determining what gets outputted to csv file.
    sel_ip = sel_name = sel_ports = sel_os = sel_lsp = sel_groups \
    = sel_location = sel_tags = sel_notes = sel_status = False

    if 'ipv4_address' in context['checks']:
        existing_header_columns.append('IPv4')
        sel_ip = True
    if 'host_name' in context['checks']:
        existing_header_columns.append('Name')
        sel_name = True
    if 'ports' in context['checks']:
        existing_header_columns.append('Ports')
        sel_ports = True
    if 'os' in context['checks']:
        existing_header_columns.append('OS')
        sel_os = True
    if 'lsp' in context['checks']:
        existing_header_columns.append('LSP')
        sel_lsp = True
    if 'host_groups' in context['checks']:
        existing_header_columns.append('Host Groups')
        sel_groups = True
    if 'location' in context['checks']:
        existing_header_columns.append('Location')
        sel_location = True
    if 'tags' in context['checks']:
        existing_header_columns.append('Tags')
        sel_tags = True
    if 'notes' in context['checks']:
        existing_header_columns.append('Notes')
        sel_notes = True
    '''# Removed status
        if 'status' in context['checks']:
        existing_header_columns.append('Status')
        sel_status = True
    '''

    ipv4_addresses = [host.ipv4_address for host in context['host_list']]
    host_names = [host.host_name for host in context['host_list']]
    open_ports = context['open_ports']
    oses = [host.os for host in context['host_list']]
    lsps = [host.lsp for host in context['host_list']]
    host_groups = [host.host_groups for host in context['host_list']]
    locations = [host.location for host in context['host_list']]
    tags = [host.tags for host in context['host_list']]
    notes = [host.notes for host in context['host_list']]
    ''' # Removed status
    statuses = [host.status for host in context['host_list']]
    '''

    host_data = zip(ipv4_addresses, host_names, oses, lsps,
                    host_groups, locations, tags, notes)

    # NOTE: Lines with #new utilize a buffer and a stream.
    #       They're great for dealing with large CSV files.
    #       Lines with #old just write lines one-by-one into the file.

    pseudo_buffer = Echo() #new
    writer = csv.writer(pseudo_buffer) #new
    #response = HttpResponse(content_type='text/csv') #old
    #writer = csv.writer(response) #old
    output = []
    output.append(existing_header_columns)

    for ip, name, os, lsp, group, loc, tag, note in host_data:
        tmp = []
        if sel_ip:
            tmp.append(ip)
        if sel_name:
            tmp.append(name)
        if sel_ports:
            if ip in open_ports:
                tmp.append(open_ports[ip])
            else:
                tmp.append('')
        if sel_os:
            tmp.append(os)
        if sel_lsp:
            tmp.append(lsp)
        if sel_groups:
            tmp.append(group)
        if sel_location:
            tmp.append(loc)
        if sel_tags:
            tmp.append(tag)
        if sel_notes:
            tmp.append(note)
        ''' Removed status
        if sel_status:
            tmp.append(status)
        '''
        output.append(tmp)
    response = StreamingHttpResponse((writer.writerow(row) for row in output),
                                        content_type="text/csv") #new
    #writer.writerows(output) #old
    response['Content-Disposition'] = 'attachment; filename="export.csv"' #new
    return response


def screenshot_host(request, subnet_id, host_id):
    host = ''
    img_name = 'host.png'
    if request.POST.get("host_to_screenshot"):
        host = request.POST.get("host_to_screenshot")
    if host:
        if host[0:4] != 'http' or host[6] != '/': # Quick way to check for http:// or https://
            host = 'http://%s' % host
        try:
            driver = webdriver.PhantomJS(executable_path="hosts/node_modules/phantomjs/bin/phantomjs")
            driver.set_window_size(512, 384)
            driver.get(host) # Goes to host's url
            driver.save_screenshot('nector_home/static/%s' % img_name)
            driver.quit()
        except WebDriverException as e:
            print '[!] Missing PhantomJS: Install into hosts/.'
            print e
            img_name = 'MISSINGPHANTOMJS'

        return detail_host(request, subnet_id, host_id, screenshot_path=img_name)

    return detail_host(request, subnet_id, host_id)
