from django.shortcuts import render, get_object_or_404
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import loader
from django.template.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required

from .models import Host
from .models import Subnet
from vulnerabilities.models import Vulnerability
from forms import HostForm

import json
import copy

import subprocess # For ping


def index(request):
    '''Renders hosts/index.html, displaying list of subnets.'''

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

    # Context to pass to hosts/index.html so we can use its key,value pairs as
    # variables in the template.
    context = {'subnet_list': sorted_subnet_qset,
               'narrowed_subnet_list' : sorted_narrowed_subnet_list,
               'narrowed_subnet_dict' : narrowed_subnet_dict}
    return render(request, 'hosts/index.html', context)


def detail(request, subnet_id):
    '''Display hosts residing on selected subnet.'''

    # Get Subnet object that was selected.
    subnet = get_object_or_404(Subnet, pk=subnet_id)

    # Break up the subnet address so we can get hosts that fall under its
    # subnet.
    address = subnet.ipv4_address

    # Get hosts that start with the same address as the subnet.
    host_list = Host.objects.filter(ipv4_address__startswith=address)

    # Context to pass to hosts/index.html so we can use its key,value pairs as
    # variables in the template.
    context = {'host_list': host_list, 'subnet_id' : subnet_id,
               'subnet' : subnet, 'limit' : 'named',}
    return render(request, 'hosts/detail.html', context)


def detail_host(request, subnet_id, host_id, ping_status=''):
    '''Display selected host information.'''

    # Get selected Host object.
    host = get_object_or_404(Host, pk=host_id)

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
                                                              port_date_list)
                  }

    else:
        # Pass context with no port information (bc host has no ports).
        context = {'host': host, 'subnet_id' : subnet_id, 'ping_status' : ping_status,
                   'vuln_list' : vuln_list, 'port_data' : None}

    return render(request, 'hosts/detail_host.html', context)


def ping(request):

    if 'host' not in request.POST:
        if 'next' in request.POST:
            return HttpResponseRedirect(request.POST['next'])


    ip = request.POST['host']
    status = subprocess.call(['ping', '-c1', '-w2', ip])

    str_status = ''
    if status == 0:
        str_status = 'Online'
    else:
        str_status = 'Offline'
    host = get_object_or_404(Host, ipv4_address=ip)
    subnet = get_object_or_404(Subnet, ipv4_address=ip.rsplit('.', 1)[0])

    return detail_host(request, subnet.id, host.id, str_status)


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


def ports(request):

    context = {}

    if request.method == "POST":

        form = request.POST
        context.update(csrf(request))

        port_numbers  = ''
        port_services = ''
        port_dates    = ''

        if 'port_nums' in request.POST:
            port_numbers = request.POST['port_nums'].strip()

        if 'port_servs' in request.POST:
            port_services = request.POST['port_servs'].strip()

        if 'port_dates' in request.POST:
            port_dates = request.POST['port_dates'].strip()

        host_list = {}

        '''# Multiple ports/services/dates feature removed
           # to prevent user confusion.
        # Check if multiple ports entered (ex 80, 443)
        if ',' in port_numbers:
            ports = port_numbers.split(',')
            context['port_list'] = ports
            # Filter each specified port, one at a time.
            for p in ports:
                p = p.strip()
                if not host_list:
                    host_list = Host.objects.filter(
                                         ports__icontains='"' + p + '"' + ':'
                                        )
                else:
                    host_list = host_list.filter(
                                             ports__icontains='"' + p + '"' + ':'
                                            )
        '''
        if port_numbers:
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


def limit_hosts(request, subnet_id):
    '''Sorts hosts when using the 'Online'/'Offline'/'All' dropdown menu
       on the Subnets page.'''

    try:
        if request.method == 'GET':

            # Get value of dropdown menu ('Online','Offline','All')
            query = request.GET.get('select_hosts', None)

            # Get Subnet object of current subnet page.
            # Use Subnet object to get the maskless IP addr
            # for obtaining the subnet's hosts.
            subnet = get_object_or_404(Subnet, pk=subnet_id)
            address = subnet.ipv4_address

            # Get queryset of (unsorted) hosts that belong to our subnet.
            host_set = Host.objects.filter(ipv4_address__startswith=address)

            # Pass queryset of hosts to helper function
            # so we can pull out each host's IP addr.
            unsorted_host_list = get_ip_list(host_set)

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

            context = {'host_list': sorted_host_set, 'limit' : query,
                       'subnet' : subnet, 'subnet_id' : subnet_id}
            return render(request, 'hosts/detail.html', context)
    except:
        return render(request, 'hosts/detail.html')


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

            # Get data entered in Search Box.
            query = request.GET.get('input_ip', None).strip()
            context = {}

            # Call helper function
            # that returns boolean
            # value based on whether
            # or not 'query' is an ip.
            if is_ip(query):

                # Get corresponding id(s) for queried IP.
                # Should only return 1 id.
                host_id_list = Host.objects.filter(ipv4_address=query)\
                                              .values_list('id', flat=True)

                # Get host object based on obtained id.
                host = get_object_or_404(Host, pk=host_id_list[0])

                # Save current host to session.
                # This will be used to see what host the user last visited.
                # Its purpose is to ensure the user is editing the right host,
                # if he/she chooses to do so.
                request.session['last-host'] = host.ipv4_address

                # Get vulnerabilities of the Host.
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

                    context = {'host': host, 'vuln_list' : vuln_list, 'port_data' : zip(port_list, port_status_list, port_info_list, port_date_list)}

                else:

                    # No ports, so don't add any port info to context.
                    context = {'host': host, 'vuln_list' : vuln_list, 'port_data' : None}

                return render(request, 'hosts/detail_host.html', context)

            # Call helper function
            # that returns boolean
            # value based on whether
            # or not 'query' is a
            # subnet.
            elif is_subnet(query):

                # Get maskless addr from query.
                ip_no_mask = query.split('/')[0]

                # Get corresponding id(s) for queried Subnet.
                # Should only return 1 subnet ID.
                subnet_id_list = Subnet.objects.filter(ipv4_address=ip_no_mask).values_list('id', flat=True)
                subnet_id = subnet_id_list[0]

                # Get Subnet object based on obtained id.
                subnet = get_object_or_404(Subnet, pk=subnet_id)

                # Get maskless subnet addr.
                address = subnet.ipv4_address.rsplit('.', 1)

                # Get list of hosts that reside in specified subnet.
                host_list = Host.objects.filter(ipv4_address__startswith=address[0])

                # Pass context and render page.
                context = {'host_list': host_list, 'limit' : 'online',
                           'subnet' : subnet, 'subnet_id' : subnet_id}
                return render(request, 'hosts/detail.html', context)

            # Assume that query
            # is a hostname:
            else:
                # Get corresponding id(s) for queried Hostname.
                # Should only return 1 host ID.
                host_id_list = Host.objects.filter(host_name__iexact=query).values_list('id', flat=True)
                host_id = host_id_list[0]

                # Get Host object based on obtained id.
                host = get_object_or_404(Host, pk=host_id)

                # Get vulnerabilities of Host.
                vuln_list = Vulnerability.objects.filter(ipv4_address=host.ipv4_address)

                # Pass context and render page.
                context = {'host': host, 'vuln_list' : vuln_list}
                return render(request, 'hosts/detail_host.html', context)

    except:
        ## Inputted query not found in our db, so load page with no host.
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
