from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
<<<<<<< Updated upstream
=======
    url(r'^edit/$', views.edit_scan, name='edit_scan'),
    url(r'^delete/$', views.delete_scan, name='delete_scan'),
>>>>>>> Stashed changes
]
