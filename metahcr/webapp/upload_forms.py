"""
 Copyright (C) 2018 Shell Global Solutions International B.V.
"""

__author__ = 'pcmarks'
from django import forms

class SGAForm(forms.Form):
    l6_upload_file = forms.FileField()

class MGAForm(forms.Form):
    scaffold_file = forms.FileField()
    gene_function_file = forms.FileField()
    rna_file = forms.FileField()

