"""nector URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from nector_home import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^about/', views.about, name='about'),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^blacklist/', include('blacklist.urls')),
    url(r'^detection/', views.detection, name='detection'),
    url(r'^events/', include('events.urls')),
    url(r'^hibp/', include('hibp.urls')),
    url(r'^hosts/', include('hosts.urls')),
    url(r'^malware/', include('malware.urls')),
    url(r'^osint/', views.osint, name='osint'),
    url(r'^reports/', views.reports, name='reports'),
    url(r'^scans/', include('scans.urls')),
    url(r'^settings/', views.settings, name='settings'),
    url(r'^status/', views.status, name='status'),
    url(r'^trending/', include('trending.urls')),
    url(r'^vulnz/', include('vulnerabilities.urls')),

]
