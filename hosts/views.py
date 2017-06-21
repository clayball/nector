from django.shortcuts import render, get_object_or_404
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


def index(request):
    '''Renders hosts/index.html, displaying list of subnets.'''

    # Get all the subnet objects.
    subnet_list = Subnet.objects.all()

    # Use this list to store subnets without their masks (aka the .0/24 piece)
    # as strings in a list.
    # We're doing this for ease of sorting.
    no_mask_list = []
    for i in subnet_list:
        no_mask_list.append(str(i).split('/')[0])

    # Sort the maskless subnets.
    sorted_subnet_list = sort_ip_list(no_mask_list)

    # Get sorted Subnet objects using sorted subnet strings.
    # (Aka "convert" list to QuerySet)
    sorted_subnet_set = []
    for s in sorted_subnet_list:
        sorted_subnet_set.append(Subnet.objects.get(ipv4_address__startswith=s))

    # Context to pass to hosts/index.html so we can use its key,value pairs as
    # variables in the template.
    context = {'subnet_list': sorted_subnet_set}
    return render(request, 'hosts/index.html', context)


def detail(request, subnet_id):
    '''Display hosts residing on selected subnet.'''

    # Get Subnet object that was selected.
    subnet = get_object_or_404(Subnet, pk=subnet_id)

    # Break up the subnet address so we can get hosts that fall under its
    # subnet.
    address = subnet.ipv4_address.rsplit('.', 1)

    # Get hosts that start with the same address as the subnet.
    host_list = Host.objects.filter(ipv4_address__startswith=address[0])

    # Context to pass to hosts/index.html so we can use its key,value pairs as
    # variables in the template.
    context = {'host_list': host_list, 'subnet_id' : subnet_id, 'limit' : 'online'}
    return render(request, 'hosts/detail.html', context)


def detail_host(request, subnet_id, host_id):
    '''Display selected host information.'''

    # Get selected Host object.
    host = get_object_or_404(Host, pk=host_id)

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
        context = {'host': host, 'subnet_id' : subnet_id,
                   'vuln_list' : vuln_list, 'port_data' : zip(port_list,
                                                              port_status_list,
                                                              port_info_list,
                                                              port_date_list)
                  }

    else:
        # Pass context with no port information (bc host has no ports).
        context = {'host': host, 'subnet_id' : subnet_id,
                   'vuln_list' : vuln_list, 'port_data' : None}

    return render(request, 'hosts/detail_host.html', context)


@login_required
# @permission_required permissions are being saved to host model -> Meta
# consider making a separate permission for each lsp
#@permission_required('hosts.edit_host', raise_exception=True)
def edit(request):
    '''Edit a host's information.'''

    # The request method used (GET, POST, etc) determines what dict 'context'
    # gets filled with.
    context = {}

    # If we have a non-empty GET request, that means the user is specifying
    # a particular host they want to edit.
    # ie They clicked the "Edit Host" button.
    if request.GET:
        # Get the respective Host object from 'host' query in URL.
        # /hosts/edit/?host=0.0.0.0
        host_ip = request.GET.get('host')
        host = get_object_or_404(Host, ipv4_address=host_ip)

        # Parse ports and port information from specified Host so we can
        # preload it into the form as string.
        str_ports = ""
        state_ports = ""
        proto_ports = ""
        date_ports = ""
        if host.ports:
            # Get Host ports as JSON object.
            json_ports = json.loads(host.ports)
            # For every port, we want port num, state, protocol, and date.
            for p in json_ports:
                # Make sure port is not an empty string
                if p:
                    str_ports += p + ', ' # Port number
                    state_ports += json_ports[p][0] + ', ' # Port state
                    proto_ports += json_ports[p][1] + ', ' # Port protocol
                    date_ports += json_ports[p][2] + ', ' # Port date

        # Load form with Host information and parsed port information.
        form = HostForm(instance=host, initial={
                                                'ports':str_ports,
                                                'port_state':state_ports,
                                                'port_protocol':proto_ports,
                                                'port_date':date_ports,
                                                })

    # If we have a non-empty POST request, that means
    # the user is submitting the form.
    elif request.POST:
        # Retrieve IP addr user entered into form.
        # Use that IP to get respective Host object.
        host_ip = request.POST['ipv4_address']
        host = get_object_or_404(Host, ipv4_address=host_ip)

        # Load form with provided information so we can save the form as
        # an object. (See forms.py and docs on ModelForms for more info)
        form = HostForm(request.POST, instance=host)

        # form.is_valid() checks that updated instance object's new attributes
        # are valid. Calling form.save() will actually save them to the db.
        if form.is_valid():

            # Get port information from POST request.
            # Each port detail will be entered as a CSV string, so we'll have
            # to parse that into JSON format.
            if request.POST['ports']:
                json_ports = ports_to_json_format(
                                                  request.POST['ports'],
                                                  request.POST['port_state'],
                                                  request.POST['port_protocol'],
                                                  request.POST['port_date']
                                                  )
                # Get a copy of the POST request so we can manipulate its values.
                post = copy.deepcopy(request.POST)
                # Store our JSON-formatted ports into our copied POST request.
                post['ports'] = json_ports
                # Create new form that follows our port formatting.
                form = HostForm(post, instance=host)

            # Save attributes from form into those of a Host object.
            form.save()

            # Get ip addr of updated Host so we can direct user to its page
            # after editing.
            new_ip = request.POST['ipv4_address']
            return HttpResponseRedirect('/hosts/search/?input_ip=%s' % new_ip)

    # Request method was empty, so user wants to create new Host.
    # Create empty form.
    else:
        form = HostForm()

    # Add new CSRF token and form to context.
    context.update(csrf(request))
    context['form'] = form
    return render(request, 'hosts/edit_host.html', context)


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
            address = subnet.ipv4_address.rsplit('.', 1)

            # Get queryset of (unsorted) hosts that belong to our subnet.
            host_set = Host.objects.filter(ipv4_address__startswith=address[0])

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

            context = {'host_list': sorted_host_set, 'limit' : query, 'subnet_id' : subnet_id}
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
                context = {'host_list': host_list, 'limit' : 'online', 'subnet_id' : subnet_id}
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
