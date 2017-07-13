from django import forms
from models import ScanType

from django.utils.translation import ugettext_lazy as _

class ScansForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ScansForm, self).__init__(*args, **kwargs)
        self.fields['scan_name'].required    = True
        self.fields['host_address'].required = True
        self.fields['ports'].required        = False
        self.fields['scan_options'].required = False

    class Meta:
        model = ScanType
        fields = ('scan_name', 'host_address', 'ports', 'scan_options')
        labels = {
            'scan_name'    : _('Scan Name'),
            'host_address' : _('Host/Subnet Address'),
            'ports'        : _('Port(s)'),
        }

        # Checkboxes for options..
        SCAN_OPTIONS_CHOICES = [
                                ('version_detection', 'Version Scan (-sV)'),
                                ('os_and_services', 'OS & Services (-A)'),
                                ('fast', 'Common Ports (-F)'),
                                ('no_ping', 'No Ping (-Pn)'),
                               ]

        widgets = {
            'scan_options' : forms.CheckboxSelectMultiple(choices=SCAN_OPTIONS_CHOICES),
            'scan_name'    : forms.TextInput(
                                    attrs={'placeholder': 'My Custom Scan 01'}
                             ),
            'host_address' : forms.TextInput(
                                    attrs={'placeholder': '104.108.168.140'}
                             ),
            'ports'        : forms.TextInput(
                                    attrs={'placeholder': '22, 80, 443, 3306'}
                             ),
        }
