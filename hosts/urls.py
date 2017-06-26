from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<subnet_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^(?P<subnet_id>[0-9]+)/host/(?P<host_id>[0-9]+)/$', views.detail_host, name='detail_host'),
    url(r'^limit-hosts/(?P<subnet_id>[0-9]+)$', views.limit_hosts, name='detail'),
    url(r'^search/$', views.search_host, name='detail_host'),
    url(r'^ping/$', views.ping, name='ping'),
    url(r'^edit/$', views.edit, name='edit'),
    url(r'^ports/$', views.ports, name='ports'),
]
