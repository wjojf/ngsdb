import os
from random import choices
import pandas as pd
from ngsdb.settings import STATIC_URL
from django import forms


class VolcanoPlotForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.df_columns = pd.read_csv(os.path.join(STATIC_URL, self.instance.data_filepath)).columns
        
    log_fold_change_column = forms.CharField(choices=[(x, x) for x in self.df_columns])
    pvalue_column = forms.CharField(choices=[(x, x) for x in self.df_columns])
