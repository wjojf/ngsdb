import django_filters
from django.contrib.contenttypes.models import ContentType
from exp.models import Descriptor, DescriptorMap, DescriptorNameValue, ExpPlatform, Experiment, ModelOrganism, Project, Sample
from django.contrib.auth.models import User


CONDITION_NAMES = {
    1: 'Condition',
    2: 'Condition2'
}


def get_condition_descriptors(n: int):
    
    try:
        descriptor_name = CONDITION_NAMES[n]
    except KeyError:
        return ()
    
    sample_descriptormaps = DescriptorMap.objects.filter(
        content_type=ContentType.objects.get_for_model(Sample)
    )
    
    sample_descriptormaps = sample_descriptormaps.filter(descriptor_name_value__desc_name__name=descriptor_name)
    
    descriptor_name_values = sample_descriptormaps.select_related('descriptor_name_value').values_list('descriptor_name_value').\
    distinct('descriptor_name_value')
    
    return DescriptorNameValue.objects.filter(pk__in=descriptor_name_values)


class ExperimentFilter(django_filters.FilterSet):
    
    experiment__project=django_filters.ModelChoiceFilter(
        field_name='experiment__project',
        queryset=Project.objects.all()
    )
    
    experiment__platform=django_filters.ModelChoiceFilter(
        field_name='experiment__platform',
        queryset=ExpPlatform.objects.all()
    )
    
    experiment__users=django_filters.ModelChoiceFilter(
        field_name='experiment__users',
        queryset=User.objects.all()
    )
    
    experiment__organism=django_filters.ModelChoiceFilter(
        field_name='experiment__organism',
        queryset=ModelOrganism.objects.all()
    )
        
    condition_1 = django_filters.ModelChoiceFilter(
        field_name='conditions__descriptor_name_value',
        queryset=get_condition_descriptors(1)
    )
    
    condition_2 = django_filters.ModelChoiceFilter(
        field_name='conditions__descriptor_name_value',
        queryset=get_condition_descriptors(2)
    )
    
    
    
    class Meta:
        model = Sample 
        exclude = ['experiment', 'sample_value']
        