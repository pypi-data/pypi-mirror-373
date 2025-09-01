from django import forms
from django.forms import HiddenInput, formset_factory


class MultipleObjectsSignForm(forms.Form):
    """
    Form for storing object signing data.
    Only the 'signature_string' field is expected, the remaining fields is service, needed for the signing scripts
    work and reverse identification of signed data
    """

    OBJECT_HASH_FIELD_NAME = 'object_hash'

    signature_string = forms.CharField(widget=HiddenInput)

    object_hash = forms.CharField(widget=HiddenInput)
    object_serialized = forms.CharField(widget=HiddenInput)
    is_detached = forms.BooleanField(widget=HiddenInput, required=False)
    signed_object_type = forms.CharField(widget=HiddenInput)


class MultipleObjectsSignCertificateForm(forms.Form):
    """
    Form for certificate data
    """

    datetime_input_formats = ['%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%d %H:%M:%S']

    cert_subject_name = forms.CharField(widget=HiddenInput)
    cert_version = forms.CharField(widget=HiddenInput, required=False)
    cert_key_algorithm = forms.CharField(widget=HiddenInput, required=False)
    cert_key_algorithm_oid = forms.CharField(widget=HiddenInput, required=False)
    cert_serial_number = forms.CharField(widget=HiddenInput, required=False)
    cert_issuer_name = forms.CharField(widget=HiddenInput, required=False)
    cert_valid_from_date = forms.DateTimeField(widget=HiddenInput, required=False, input_formats=datetime_input_formats)
    cert_valid_to_date = forms.DateTimeField(widget=HiddenInput, required=False, input_formats=datetime_input_formats)


MultipleObjectsSignFormSet = formset_factory(MultipleObjectsSignForm, extra=0)
