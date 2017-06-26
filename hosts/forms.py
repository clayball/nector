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
        self.fields['status'].required       = True


    class Meta:
        model = Host
        fields = ('host_name', 'os', 'location',
                  'tags', 'host_groups', 'notes', 'status')
        labels = {
            'host_name'   : _('Host Name'),
            'os'          : _('OS'),
            'location'    : _('Location'),
            'tags'        : _('Tag(s)'),
            'host_groups' : _('Host Group(s)'),
            'notes'       : _('Note(s)'),
            'status'      : _('* Status'),
        }
        # Radio buttons for status.
        CHOICES = (('Online', 'Online',), ('Offline', 'Offline',))
        widgets = {
            'host_name'     : forms.TextInput(attrs={'placeholder':'conficturaindustries.com'}),
            'status'        : forms.RadioSelect(choices=CHOICES),
        }
