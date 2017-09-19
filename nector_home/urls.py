from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^status/', views.status, name='status'),
    url(r'^setup-hosts/', views.status_setup_hosts, name='status_setup_hosts'),
    url(r'^setup-ports/', views.status_setup_ports, name='status_setup_ports'),
    url(r'^setup-events/', views.status_setup_events, name='status_setup_events'),
    url(r'^setup-vulns/', views.status_setup_vulns, name='status_setup_vulns'),
    url(r'^setup-malware/', views.status_setup_malware, name='status_setup_malware'),

    url(r'^submit-subnets/', views.submit_subnets, name='submit_subnets'),
    url(r'^nmap-hosts/', views.nmap_hosts, name='nmap_hosts'),
    url(r'^nmap-ports/', views.nmap_ports, name='nmap_ports'),
    url(r'^submit-hosts/', views.submit_hosts, name='submit_hosts'),
    url(r'^submit-ports/', views.submit_ports, name='submit_ports'),
    url(r'^submit-events/', views.submit_events, name='submit_events'),
    url(r'^submit-vulns/', views.submit_vulns, name='submit_vulns'),
    url(r'^submit-malware/', views.submit_malware, name='submit_malware'),
]
