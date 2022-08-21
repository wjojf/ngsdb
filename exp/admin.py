from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from exp import models as exp_models
from exp.forms import DescriptorMapInlineForm

# Register your models here.

# Experiment models 
admin.site.register(exp_models.ExpPlatform)
admin.site.register(exp_models.Project)
admin.site.register(exp_models.PrepMethod)


# EAV Concept Models
admin.site.register(exp_models.Descriptor)
admin.site.register(exp_models.DescriptorValue)

class DescriptorMapAdmin(admin.ModelAdmin):
    model = exp_models.DescriptorMap
    list_display = ('desc_name', 'desc_value', 'content_type', 'object_id', 'object')
    readonly_fields = ('object', )

admin.site.register(exp_models.DescriptorMap, DescriptorMapAdmin)


#         --------------Inlines------------

class DescriptorMapInline(GenericTabularInline):
    model = exp_models.DescriptorMap
    form = DescriptorMapInlineForm
    classes = ['extrapretty']
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


class SampleInline(admin.StackedInline):
    model = exp_models.Sample
    classes = ['wide', 'collapse', 'extrapretty']
    extra = 0

@admin.register(exp_models.Sample)
class SampleAdmin(admin.ModelAdmin):
    model = exp_models.Sample
    inlines = [DescriptorMapInline] 


class ExperimentAdmin(admin.ModelAdmin):
    model = exp_models.Experiment
    inlines = [SampleInline]
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