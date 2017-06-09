from django import forms

class ScansForm(forms.Form):
    ipv4_address = forms.CharField(label='IPv4 Address', max_length=15, required=False,
                    #    widget=forms.TextInput(
                    #        attrs={'placeholder': '104.108.168.140'}
                    #    )
    )
    host_name = forms.CharField(label='Host Name', max_length=80, required=False,
                    #    widget=forms.TextInput(
                    #        attrs={'placeholder': 'conficturaindustries.com'}
                    #    )
    )
    os = forms.CharField(label='OS', max_length=50, required=False,
                    #    widget=forms.TextInput(
                    #        attrs={'placeholder': 'Windows'}
                    #    )
    )
    lsp = forms.CharField(label='LSP', max_length=50, required=False,
                    #    widget=forms.TextInput(
                    #        attrs={'placeholder': 'E-Corp'}
                    #    )
    )
    location = forms.CharField(label='Location', max_length=25, required=False,
                    #    widget=forms.TextInput(
                    #        attrs={'placeholder': 'New York'}
                    #    )
    )
    tags = forms.CharField(label='Tag(s)', max_length=50, required=False,
                    #    widget=forms.TextInput(
                    #        attrs={'placeholder': 'books'}
                    #    )
    )
    host_groups = forms.CharField(label='Host Group(s)', max_length=125, required=False,
                    #    widget=forms.TextInput(
                    #        attrs={'placeholder': 'E-Servers'}
                    #    )
    )
    notes = forms.CharField(label='Note(s)', max_length=320, required=False,
                    #    widget=forms.TextInput(
                    #        attrs={'placeholder': 'Online'}
                    #    )
    )
    ports = forms.CharField(label='Open Port(s)', max_length=50, required=False,
                    #    widget=forms.TextInput(
                    #        attrs={'placeholder': '80'}
                    #    )
    )
