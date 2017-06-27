from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^addfeed/$', views.add_feed, name='addfeed'),
    url(r'^removefeed/$', views.remove_feed, name='removefeed'),
]
