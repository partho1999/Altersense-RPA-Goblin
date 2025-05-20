# forms.py
from django import forms
from multiupload.fields import MultiFileField
from apps.commercial.models import PurchaseFile, InvoiceFile


class PurchaseForm(forms.ModelForm):
    file = MultiFileField(min_num=1, max_num=200, max_file_size=1024 *
                          1024*5, help_text='You can upload up to 200 files')

    class Meta:
        model = PurchaseFile
        fields = ['file']


class InvoiceForm(forms.ModelForm):
    file = MultiFileField(min_num=1, max_num=200, max_file_size=1024 *
                          1024*5, help_text='You can upload up to 200 files')

    class Meta:
        model = InvoiceFile
        fields = ['file']
