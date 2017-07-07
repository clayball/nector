from django import forms

class ScansForm(forms.Form):
    scan_name = forms.CharField(label='Scan Name', max_length=255, required=True,
                        widget=forms.TextInput(
                            attrs={'placeholder': 'My Custom Scan 01'}
                        )
    )
    host_address = forms.CharField(label='Host/Subnet Address', max_length=30, required=True,
                        widget=forms.TextInput(
                            attrs={'placeholder': '104.108.168.140'}
                        )
    )
    ports = forms.CharField(label='Port(s)', max_length=255, required=False,
                        widget=forms.TextInput(
                            attrs={'placeholder': '22, 80, 443, 3306'}
                        )
    )

    SCAN_TYPE_CHOICES = [
               ('list_scan', 'List Scan (-sL)'),
               ('no_port_scan', 'No Port Scan (-sn)'),
               ('ping', 'Ping Scan (-sP)'),
               ('no_ping', 'No Ping Scan (-Pn)'),
               ('version_detection', 'Version Scan (-sV)'),
    ]

    scan_type = forms.ChoiceField(choices=SCAN_TYPE_CHOICES,
                                  widget=forms.RadioSelect,
                                  required=True,
    )

    SCAN_OPTIONS_CHOICES = [
                            ('os_and_services', 'OS & Services (-A)'),
                            ('fast', 'Common Ports (-F)')]

    scan_options = forms.MultipleChoiceField(choices=SCAN_OPTIONS_CHOICES,
                                             widget=forms.CheckboxSelectMultiple()
    )
