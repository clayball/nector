from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^edit/$', views.edit_scan, name='edit_scan'),
    url(r'^perform/$', views.perform_scan, name='perform_scan'),
    url(r'^delete/$', views.delete_scan, name='delete_scan'),
]
