from django import forms
from models import Host

class HostForm(forms.ModelForm):

    class Meta:
        model = Host
        #fields = ('ipv4_address', 'host_name')
        fields = "__all__"
