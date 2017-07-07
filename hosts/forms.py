from django import forms
from models import Host
from django.utils.translation import ugettext_lazy as _

class HostForm(forms.ModelForm):


    def __init__(self, *args, **kwargs):
        super(HostForm, self).__init__(*args, **kwargs)
        self.fields['host_name'].required    = False
        self.fields['os'].required           = False
        self.fields['location'].required     = False
        self.fields['tags'].required         = False
        self.fields['host_groups'].required  = False
        self.fields['notes'].required        = False
        #self.fields['status'].required       = True


    class Meta:
        model = Host
        fields = ('host_name', 'os', 'location',
                  'tags', 'host_groups', 'notes')
        labels = {
            'host_name'   : _('Host Name'),
            'os'          : _('OS'),
            'location'    : _('Location'),
            'tags'        : _('Tag(s)'),
            'host_groups' : _('Host Group(s)'),
            'notes'       : _('Note(s)'),
            #'status'      : _('* Status'),
        }
        # Radio buttons for status.
        CHOICES = (('Online', 'Online',), ('Offline', 'Offline',))
        widgets = {
            'host_name'     : forms.TextInput(attrs={'placeholder':'conficturaindustries.com'}),
            #'status'        : forms.RadioSelect(choices=CHOICES),
        }


class SearchForm(forms.Form):
    ipv4_address = forms.CharField(label='IPv4 Address', max_length=15, required=False,
                        widget=forms.TextInput(
                            attrs={'placeholder': '104.108.168.140'}
                        )
    )
    host_name = forms.CharField(label='Host Name', max_length=80, required=False,
                        widget=forms.TextInput(
                            attrs={'placeholder': 'conficturaindustries.com'}
                        )
    )
    os = forms.CharField(label='OS', max_length=50, required=False,
                        widget=forms.TextInput(
                            attrs={'placeholder': 'Ubuntu'}
                        )
    )
    lsp = forms.CharField(label='LSP', max_length=50, required=False,
                        widget=forms.TextInput(
                            attrs={'placeholder': 'E-Corp'}
                        )
    )
    location = forms.CharField(label='Location', max_length=25, required=False,
                        widget=forms.TextInput(
                            attrs={'placeholder': 'New York'}
                        )
    )
    tags = forms.CharField(label='Tag(s)', max_length=50, required=False,
                        widget=forms.TextInput(
                            attrs={'placeholder': 'books'}
                        )
    )
    host_groups = forms.CharField(label='Host Group(s)', max_length=125, required=False,
                        widget=forms.TextInput(
                            attrs={'placeholder': 'E-Servers'}
                        )
    )
    notes = forms.CharField(label='Note(s)', max_length=320, required=False,
                        widget=forms.TextInput(
                            attrs={'placeholder': 'Online'}
                        )
    )
    ports = forms.CharField(label='Open Port(s)', max_length=50, required=False,
                        widget=forms.TextInput(
                            attrs={'placeholder': '80'}
                        )
    )
    services = forms.CharField(label='Service', max_length=50, required=False,
                        widget=forms.TextInput(
                            attrs={'placeholder': 'Apache'}
                        )
    )
