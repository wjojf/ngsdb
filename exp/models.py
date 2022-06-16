from django.db import models
from django.contrib.auth.models import User


# Create your models here.

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


class ModelOrganism(models.Model):
    
    def __str__(self):
        return f'{self.id}'

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