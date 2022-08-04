import django_filters
from django.contrib.contenttypes.models import ContentType
from exp.models import Descriptor, DescriptorMap, Experiment


class ExperimentFilter(django_filters.FilterSet):
    
    conditions = django_filters.ModelChoiceFilter(
        queryset=DescriptorMap.objects.filter(
            content_type=ContentType.objects.get_for_model(Experiment)
        )
    )

    class Meta:
        model = Experiment
        fields = '__all__'
        exclude = ['data_filepath', 'metadata_filepath']