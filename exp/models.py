from tabnanny import verbose
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType

########################
#     Managers         #
########################

class OrganismMapManager(models.Manager):
    def update_for_object(self, obj, **kwargs):
        '''
        Sets custom field types and their values for obj.
        kwargs provides Descriptor:DescriptorValue pairs.
        If the provided Descriptor or DescriptorValue does not exist
        it will be created.
        '''

        current_organism = self.get_for_object(
            obj).values_list('organism_name__name', flat=True)

        for organism, organism_val in kwargs.items():
            org = organism.lower()
            if org in current_organism and organism_val == '':
                OrganismValue._default_manager.remove_for_object(obj, org)
            else:
                # FIXME: This is bad, because it doesn't check if field_val is the same...
                # But it is enforced at the database level through unique constraints.
                OrganismValue._default_manager.add_for_object(
                    obj, org, organism_val)

    def get_by_model(self, queryset_or_model, filters={}):
        try:
            queryset = queryset_or_model._default_manager.objects.all()
        except AttributeError:
            queryset = queryset_or_model
        # FIXME: ``organism`` is hardcoded here - needs to be changed!
        organism = filters.get('organism', '')
        
        organism_value_qs = OrganismValue.objects.filter(
            value__icontains=filters.get('value', ''), organism=organism)
        
        organism_value = self.filter(organism_value__in=organism_value_qs, organism_name=organism,
                                 object_id__in=queryset.values_list('id', flat=True))
        return [ct.object for ct in organism_value]


class OrganismValueManager(models.Manager):
    
    def remove_for_object(self, obj, organism_name, val=None):
        if val is not None:
            OrganismMap._default_manager.get_for_object(obj).filter(
                organism_name__name=organism_name, organism_value__value=val).delete()
        else:
            OrganismMap._default_manager.get_for_object(obj).filter(
                organism_name__name=organism_name).delete()

    def add_for_object(self, obj, organism_name, val):
        '''
        Creates new custom OrganismValue for a given obj and Organism.
        '''
        organism, created = Organism._default_manager.get_or_create(
            name=organism_name)
        value, created = self.get_or_create(value=val, organism=organism)
        ctype = ContentType.objects.get_for_model(obj)
        
        OrganismMap._default_manager.get_or_create(
            organism_name=organism_name,
            organism_value=value,
            content_type=ctype,
            object_id=obj.pk
        )



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

class Organism(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    class Meta:
        verbose_name = 'organism'
    
    def __str__(self):
        return f'{self.name}'


class OrganismValue(models.Model):
    
    organism = models.ForeignKey(Organism, on_delete=models.CASCADE)
    value = models.CharField(db_index=True, max_length=255)
    
    objects = OrganismValueManager()

    class Meta:
        unique_together = ('organism', 'value')
    
    
class OrganismMap(models.Model):
    organism = models.ForeignKey(
        Organism,
        db_index=True,
        on_delete=models.CASCADE
    )
    
    organism_value = models.ForeignKey(
        OrganismValue,
        db_index=True,
        on_delete=models.CASCADE
    )
    
    content_type = models.ForeignKey(
        ContentType,
        verbose_name='model organism',
        db_index=True,
        on_delete=models.CASCADE
    )
    
    object_id = models.PositiveIntegerField(db_index=True)
    object = GenericForeignKey('content_type', 'object_id')

    objects = OrganismMapManager()


class ModelOrganism(models.Model):
    name = models.CharField(max_length=200)
    custom_fields = GenericRelation(OrganismMap)
    
    def __str__(self):
        return f'{self.name}'


#####################
#   Final Model     #
#####################


class Experiment(models.Model):
    data_filepath = models.CharField(max_length=250)
    project = models.ForeignKey(Project, null=True ,on_delete=models.SET_NULL) 
    platform = models.ForeignKey(ExpPlatform, null=True, on_delete=models.SET_NULL)
    users = models.ManyToManyField(User,blank=True)
    organism = models.ForeignKey(ModelOrganism, null=True, on_delete=models.SET_NULL)
    prep_method = models.ForeignKey(PrepMethod, null=True, on_delete=models.SET_NULL)
    conditions = {} # how to handle conditions?

    def __str__(self):
        return f'Exp {self.id} \n {self.data_filepath}'