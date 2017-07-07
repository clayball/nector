from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<subnet_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^(?P<subnet_id>[0-9]+)/host/(?P<host_id>[0-9]+)/$', views.detail_host, name='detail_host'),
    url(r'^search/$', views.search_host, name='detail_host'),
    url(r'^ping/$', views.ping, name='ping'),
    url(r'^edit/$', views.edit, name='edit'),
    url(r'^ports/$', views.ports, name='ports'),
    url(r'^alerts/$', views.alerts, name='alerts'),
    url(r'^custom-search/$', views.search, name='search'),
    url(r'^export/$', views.export, name='export'),
]
