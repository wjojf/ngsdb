import django_filters
from exp.models import Experiment


class ExperimentFilter(django_filters.FilterSet):
    
    class Meta:
        model = Experiment
        fields = '__all__'
        exclude = ['data_filepath', 'metadata_filepath']