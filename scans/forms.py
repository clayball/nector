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
