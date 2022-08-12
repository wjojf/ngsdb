from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from exp import models as exp_models
from exp.forms import DescriptorMapInline

# Register your models here.

# Experiment models 
admin.site.register(exp_models.ExpPlatform)
admin.site.register(exp_models.Project)
admin.site.register(exp_models.PrepMethod)


# EAV Concept Models
admin.site.register(exp_models.Descriptor)
admin.site.register(exp_models.DescriptorValue)
admin.site.register(exp_models.DescriptorMap)


#         --------------Inlines------------
class DescriptorMapInline(GenericTabularInline):
    model = exp_models.DescriptorMap
    form = DescriptorMapInline
    classes = ['wide', 'collapse']
    extra = 1
    

#    ----------------------------------------

class ModelOrganismAdmin(admin.ModelAdmin):
    model = exp_models.ModelOrganism
    inlines = [DescriptorMapInline]
    fieldsets = (
        ('Standard info', {
            'fields': ['name']
        }),
    )

admin.site.register(exp_models.ModelOrganism, ModelOrganismAdmin)


class ExperimentAdmin(admin.ModelAdmin):
    model = exp_models.Experiment
    inlines = [DescriptorMapInline]
    exclude = ['conditions', ]
    fieldsets = (
        
        ('Files', {
            'classes': ['wide', 'extrapretty'],
            'fields': ['metadata_filepath', 'data_filepath']
            }
        ),
        
        ('Metadata', {
                'classes': ['wide'],
                'fields': ['project', 'platform', 'organism', 'prep_method']
            }
        ),
        
    )

admin.site.register(exp_models.Experiment, ExperimentAdmin)