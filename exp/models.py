from django.db import models
from django.db.models.signals import post_delete
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from exp.singals_utils import file_cleanup, exp_directory_cleanup
import os


#####################
#       Models      #
#####################

class HandledDirectory(models.Model):
    directory_name = models.CharField(verbose_name='Experiment Directory', max_length=200, unique=True)
    
    class Meta:
        verbose_name_plural = 'Experiment Directories'
    
    def __str__(self):
        return str(self.directory_name)


class Project(models.Model):
    title = models.CharField(max_length=150, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    def __str__(self):
        return f'{self.title}'


class PrepMethod(models.Model):
    method = models.CharField(max_length=150, default='')
    kit = models.CharField(max_length=150, default='')

    class Meta:
        unique_together = ('method', 'kit')
    

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
    value = models.CharField(db_index=True, max_length=255, unique=True)

    def __str__(self):
        return self.value


class DescriptorNameValue(models.Model):
    desc_name = models.ForeignKey(Descriptor, on_delete=models.CASCADE)
    desc_value = models.ForeignKey(DescriptorValue, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('desc_name', 'desc_value')
    
    def __str__(self):
        return f'{self.desc_name}:={self.desc_value}'


class DescriptorMap(models.Model):

    descriptor_name_value = models.ForeignKey(
        DescriptorNameValue,
        verbose_name='Descriptor Name & Value Pair',
        on_delete=models.CASCADE,
        default=None
    )
    
    content_type = models.ForeignKey(
        ContentType, verbose_name='Content Type', db_index=True, on_delete=models.CASCADE)
    
    object_id = models.PositiveIntegerField(db_index=True)
    
    object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = ('descriptor_name_value',
                           'content_type', 'object_id')

    def __str__(self):
        return str(self.descriptor_name_value)


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


#####################
# Experiment Model #
#####################


def experiment_data_filepath(instance, filename):
    # file will be uploaded to MEDIA_ROOT/fileformat
    file_format = filename.split('.')[-1]
    filename = os.path.basename(filename)
    return f'{file_format}/{filename}'


class Experiment(models.Model):
    
    exp_directory = models.ForeignKey(HandledDirectory, on_delete=models.CASCADE, verbose_name='Experiment Directory', null=True)
    
    project = models.ForeignKey(
        Project, null=True, on_delete=models.SET_NULL, verbose_name='Experiment Project')
    
    platform = models.ForeignKey(
        ExpPlatform, null=True, on_delete=models.SET_NULL, verbose_name='Experiment Platform')
    
    users = models.ManyToManyField(User, blank=True, verbose_name='Users')
    
    organism = models.ForeignKey(
        ModelOrganism, null=True, on_delete=models.SET_NULL, verbose_name='Model Organism')
    
    prep_method = models.ForeignKey(
        PrepMethod, null=True, on_delete=models.SET_NULL, verbose_name='Preparation Method')
    
    
    def __str__(self):
        return f'Experiment {self.id}'

post_delete.connect(
    exp_directory_cleanup,
    sender=Experiment,
    dispatch_uid="Experiment.exp_directory_cleanup"
)

################
# Sample model #
################


class Sample(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    sample_value = models.CharField(max_length=100, verbose_name='Sample ID')
    conditions = GenericRelation(DescriptorMap)


    def __str__(self):
        return f'{self.experiment} - {self.sample_value}'


class ExperimentFile(models.Model):
    TYPE_CHOICES = [ 
        ('nextseq', 'NextSeq'),
        ('deseq', 'Deseq'),
        ('count_matrix', 'CountMatrix')
    ]
    
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    file_type = models.CharField(max_length=150,choices=TYPE_CHOICES, verbose_name='File Type')
    file_instance = models.FileField(upload_to=experiment_data_filepath)
    
    @property
    def is_nextseq(self):
        return self.file_type == 'nextseq'
    
    @property
    def is_deseq(self):
        return self.file_type == 'deseq'
    
    @property
    def is_count_matrix(self):
        return self.file_type == 'count_matrix'
    
    def get_absolute_url(self):
        if self.is_deseq:
            return reverse('volcano-plot', kwargs={"file_id": self.id})
        elif self.is_count_matrix:
            return reverse('pca-plot', kwargs={"file_id": self.id})
        return '/'

    def __str__(self):
        return f'{self.file_type} - {self.experiment}'

post_delete.connect(file_cleanup, sender=ExperimentFile, dispatch_uid="ExperimentFile.file_cleanup")