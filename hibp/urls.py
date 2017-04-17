from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^account/$', views.check_pwn_account, name='pwnaccount'),
]
