from pyexpat import model
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

########################
#     Managers         #
########################


class DescriptorMapManager(models.Manager):
    '''
    Corresponds to TaxonomyManager in django-taxonomy.
    '''

    def update_for_object(self, obj, **kwargs):
        '''
        Sets custom field types and their values for obj.
        kwargs provides Descriptor:DescriptorValue pairs.
        If the provided Descriptor or DescriptorValue does not exist
        it will be created.
        '''

        current_desc = self.get_for_object(
            obj).values_list('desc_name__name', flat=True)

        for desc, desc_val in kwargs.items():
            d = desc.lower()
            if d in current_desc and desc_val == '':
                DescriptorValue._default_manager.remove_for_object(obj, d)
            else:
                # FIXME: This is bad, because it doesn't check if field_val is the same...
                # But it is enforced at the database level through unique constraints.
                DescriptorValue._default_manager.add_for_object(
                    obj, d, desc_val)

    def get_by_model(self, queryset_or_model, filters={}):

        try:
            queryset = queryset_or_model._default_manager.objects.all()
        except AttributeError:
            queryset = queryset_or_model
        # FIXME: ``descriptor`` is hardcoded here - needs to be changed!
        desc = filters.get('descriptor', '')
        desc_value_qs = DescriptorValue.objects.filter(
            value__icontains=filters.get('value', ''), descriptor=desc)
        desc_value = self.filter(desc_value__in=desc_value_qs, desc_name=desc,
                                 object_id__in=queryset.values_list('id', flat=True))
        return [ct.object for ct in desc_value]

    def get_for_object(self, obj):
        '''
        Retrieves DescriptorMap instances for given object.
        '''
        ctype = ContentType.objects.get_for_model(obj)
        return self.filter(content_type__pk=ctype.pk, object_id=obj.pk)


class DescriptorValueManager(models.Manager):

    def remove_for_object(self, obj, desc_name, val=None):
        if val is not None:
            DescriptorMap._default_manager.get_for_object(obj).filter(
                desc_name__name=desc_name, desc_value__value=val).delete()
        else:
            DescriptorMap._default_manager.get_for_object(obj).filter(
                desc_name__name=desc_name).delete()

    def add_for_object(self, obj, desc_name, val):
        '''
        Creates new custom DescriptorValue for a given obj and Descriptor.
        '''
        desc, created = Descriptor._default_manager.get_or_create(
            name=desc_name)
        value, created = self.get_or_create(value=val, desriptor=desc)
        ctype = ContentType.objects.get_for_model(obj)
        DescriptorMap._default_manager.get_or_create(
            desc_name=desc, desc_value=value, content_type=ctype, object_id=obj.pk)


#####################
#       Models      #
#####################

class Project(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    def __str__(self):
        return f'{self.title}'


class PrepMethod(models.Model):
    method = models.CharField(max_length=150, default='')
    kit = models.CharField(max_length=150, default='')

    def __str__(self):
        return f'Method: {self.method} \n Kit: {self.kit}'


class ExpPlatform(models.Model):
    title = models.CharField(max_length=150)
    n_reads = models.IntegerField()
    length_libtype = models.CharField(max_length=150)

    def __str__(self):
        return f'{self.title}-{self.n_reads}-{self.length_libtype}'

##############################
#   EAV for ModelOrganism    #
##############################


class Descriptor(models.Model):
    '''
    Custom descriptor. Previously FieldTaxonomy.
    Corresponds to Taxonomy in django-taxonomy.
    '''

    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = 'descriptor'

    def __str__(self):
        return self.name


class DescriptorValue(models.Model):
    '''
    Values of custom descriptors are stored here.
    Previously FieldValue
    Corresponds to TaxonomyTerm in django-taxonomy.
    '''
    descriptor = models.ForeignKey(Descriptor, on_delete=models.CASCADE)
    value = models.CharField(db_index=True, max_length=255)

    objects = DescriptorValueManager()

    class Meta:
        unique_together = ('descriptor', 'value')

    def __str__(self):
        return self.value


class DescriptorMap(models.Model):
    '''
    Mapping between content (Model Organism) and custom descriptors/values.
    Previously FieldTaxonomyMap.
    Corresponds to TaxonomyMap in django-taxonomy.
    '''
    desc_value = models.ForeignKey(DescriptorValue, db_index=True,
                                   on_delete=models.CASCADE)
    desc_name = models.ForeignKey(Descriptor, db_index=True,
                                  on_delete=models.CASCADE)
    content_type = models.ForeignKey(
        ContentType, verbose_name='Django Model', db_index=True, on_delete=models.CASCADE)
    
    object_id = models.PositiveIntegerField(db_index=True)
    
    object = GenericForeignKey('content_type', 'object_id')

    objects = DescriptorMapManager()

    class Meta:
        unique_together = ('desc_value', 'desc_name',
                           'content_type', 'object_id')

    def __str__(self):
        return f'[{self.content_type}] {self.desc_name} = {self.desc_value}'


class ModelOrganism(models.Model):
    
    NAME_OPTS = [
        ('human', 'Human'),
        ('bacteria', 'Bacteria'),
        ('mouse', 'Mouse'),
        ('c.elegans', 'Caenorhabditis elegans')
    ]
    
    name = models.CharField(verbose_name='Organism type', max_length=200, choices=NAME_OPTS)
    custom_fields = GenericRelation(DescriptorMap)
    
   
    def __str__(self):
        return f"{self.name} #{self.id}"


class ExpConditions(models.Model):
    custom_fields = GenericRelation(DescriptorMap)

    def __str__(self):
        return f'Conditions Set # {self.id}'


#####################
#   Final Model     #
#####################
def experiment_data_filepath(instance, filename):
    # file will be uploaded to MEDIA_ROOT/fileformat
    file_format = filename.split('.')[-1]
    return f'{file_format}/{filename}'


class Experiment(models.Model):
    
    metadata_filepath = models.FileField(verbose_name='Metadata file', upload_to=experiment_data_filepath, null=False, default='Not Avaliable')
    data_filepath = models.FileField(verbose_name='Results file', upload_to=experiment_data_filepath, null=False, default='Not Avaliable')
    
    project = models.ForeignKey(
        Project, null=True, on_delete=models.SET_NULL, verbose_name='Experiment Project')
    
    platform = models.ForeignKey(
        ExpPlatform, null=True, on_delete=models.SET_NULL, verbose_name='Experiment Platform')
    
    users = models.ManyToManyField(User, blank=True, verbose_name='Users')
    
    organism = models.ForeignKey(
        ModelOrganism, null=True, on_delete=models.SET_NULL, verbose_name='Model Organism')
    
    prep_method = models.ForeignKey(
        PrepMethod, null=True, on_delete=models.SET_NULL, verbose_name='Preparation Method')
    
    conditions = models.ForeignKey(
        ExpConditions, null=True, on_delete=models.SET_NULL, verbose_name='Experiment Conditions')

    def __str__(self):
        return f'Exp {self.id} \n {self.data_filepath}'
    