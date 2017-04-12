from django.contrib import admin

# Register your models here.
from .models import Subnet
from .models import Host

admin.site.register(Subnet)
admin.site.register(Host)
