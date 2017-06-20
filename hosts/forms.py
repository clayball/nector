from django import forms
from models import Host
from django.utils.translation import ugettext_lazy as _

class HostForm(forms.ModelForm):

    port_state = forms.CharField(label='State(s)', required=False,
                                 widget=forms.TextInput(attrs={'placeholder': 'open, closed'}))
    port_protocol = forms.CharField(label='Protocol(s)', required=False,
                                 widget=forms.TextInput(attrs={'placeholder': 'Apache2, Apache2'}))
    port_date = forms.CharField(label='Date(s)', required=False,
                                 widget=forms.TextInput(attrs={'placeholder': '170424, 170509'}))

    def __init__(self, *args, **kwargs):
        super(HostForm, self).__init__(*args, **kwargs)
        self.fields['ipv4_address'].required = True
        self.fields['host_name'].required    = False
        self.fields['os'].required           = False
        self.fields['lsp'].required          = False
        self.fields['location'].required     = False
        self.fields['tags'].required         = False
        self.fields['host_groups'].required  = False
        self.fields['notes'].required        = False
        self.fields['ports'].required        = False
        self.fields['status'].required       = True

    class Meta:
        model = Host
        fields = ('ipv4_address', 'host_name', 'os', 'lsp', 'location',
                  'tags', 'host_groups', 'notes', 'ports', 'status')
        labels = {
            'ipv4_address': _('* IPv4 Address'),
            'host_name'   : _('Host Name'),
            'os'          : _('OS'),
            'lsp'         : _('LSP'),
            'location'    : _('Location'),
            'tags'        : _('Tag(s)'),
            'host_groups' : _('Host Group(s)'),
            'notes'       : _('Note(s)'),
            'ports'       : _('Port(s)'),
            'status'      : _('* Status'),
        }
        # Radio buttons for status.
        CHOICES = (('Online', 'Online',), ('Offline', 'Offline',))
        widgets = {
            'ipv4_address'  : forms.TextInput(attrs={'placeholder':'0.0.0.0'}),
            'host_name'     : forms.TextInput(attrs={'placeholder':'conficturaindustries.com'}),
            'ports'         : forms.TextInput(attrs={'placeholder':'80, 443'}),
            'status'        : forms.RadioSelect(choices=CHOICES),
        }
