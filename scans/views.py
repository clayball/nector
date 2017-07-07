from django.shortcuts import render

from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.template.context_processors import csrf
from django.template import loader

from forms import ScansForm


def index(request):
    '''
    Default search page.
    If a POST request was made to get here, then our form was submitted,
    so display a table of the query made.
    Otherwise, just display the form.
    '''

    live_scanning = False

    if request.POST.get("live_scan"):
        # User pressed Export button.
        live_scanning = True

    if request.method == "POST":
        # User is either Generating a table to the page (exporting=False)
        #             or Exporting to a CSV file (exporting=True).

        # Get form information.
        form = ScansForm(request.POST)

        if form.is_valid():

            # Append important info to context.
            context = {}

            context.update(csrf(request))
            context['form'] = form

            # If we're exporting, export!
            if exporting:
                return export(request, context)

            # We're not exporting, so render the page with a table.
            return render(request, 'scans/scans.html', context)

    context = {}
    context.update(csrf(request))
    context['form'] = ScansForm()
    context['checks'] = ['ipv4_address', 'host_name', 'ports']
    return render(request, 'scans/scans.html', context)
