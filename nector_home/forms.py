from django import forms
from events.models import Event
from vulnerabilities.models import Vulnerability
from django.utils.translation import ugettext_lazy as _

class EventForm(forms.ModelForm):


    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.fields['request_number'].required    = False
        self.fields['date_submitted'].required             = False
        self.fields['title'].required    = False
        self.fields['status'].required            = False
        self.fields['date_last_edited'].required  = False
        self.fields['submitters'].required        = False
        self.fields['assignees'].required         = False


    class Meta:
        model = Event
        fields = ('request_number', 'date_submitted', 'title',
                  'status', 'date_last_edited', 'submitters', 'assignees')
        labels = {
            'request_number'   : _(''),
            'date_submitted'   : _(''),
            'title'            : _(''),
            'status'           : _(''),
            'date_last_edited' : _(''),
            'submitters'       : _(''),
            'assignees'        : _(''),
        }

        widgets = {
            'request_number'   : forms.TextInput(attrs={'placeholder':'1234', 'size' : '10'}),
            'date_submitted'   : forms.TextInput(attrs={'placeholder':'04/24/2017', 'size' : '10'}),
            'title'            : forms.TextInput(attrs={'placeholder':'Server 0.0.0.0 has malware: Backdoor-FFBM', 'size' : '45'}),
            'status'           : forms.TextInput(attrs={'placeholder':'Open', 'size' : '6'}),
            'date_last_edited' : forms.TextInput(attrs={'placeholder':'05/09/2017', 'size' : '10'}),
            'submitters'       : forms.TextInput(attrs={'placeholder':'Tyrell of E-Corp', 'size' : '12'}),
            'assignees'        : forms.TextInput(attrs={'placeholder':'All-Safe Security', 'size' : '12'}),
        }




class VulnForm(forms.ModelForm):


    def __init__(self, *args, **kwargs):
        super(VulnForm, self).__init__(*args, **kwargs)
        #self.fields['plugin_and_host'].required = False
        self.fields['plugin_id'].required       = False
        self.fields['plugin_name'].required     = False
        self.fields['severity'].required        = False
        self.fields['ipv4_address'].required    = False
        self.fields['host_name'].required       = False


    class Meta:
        model = Vulnerability
        fields = ('plugin_id', 'plugin_name',
                  'severity', 'ipv4_address', 'host_name')
        labels = {
            'plugin_id'       : _(''),
            'plugin_name'     : _(''),
            'severity'        : _(''),
            'ipv4_address'    : _(''),
            'host_name'       : _(''),
        }

        widgets = {
            'plugin_id'       : forms.TextInput(attrs={'placeholder':'12345', 'size' : '10'}),
            'plugin_name'     : forms.TextInput(attrs={'placeholder':'uBlock Origin 1.13.8', 'size' : '35'}),
            'severity'        : forms.TextInput(attrs={'placeholder':'Medium', 'size' : '8'}),
            'ipv4_address'    : forms.TextInput(attrs={'placeholder':'0.0.0.0', 'size' : '20'}),
            'host_name'       : forms.TextInput(attrs={'placeholder':'brians-pc.example.com', 'size' : '30'}),
        }
