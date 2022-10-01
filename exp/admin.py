from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from exp import models as exp_models
from exp.forms import DescriptorMapInlineForm


# Experiment models 
admin.site.register(exp_models.HandledDirectory)
admin.site.register(exp_models.ExperimentFile)
admin.site.register(exp_models.ExpPlatform)
admin.site.register(exp_models.Project)
admin.site.register(exp_models.PrepMethod)



# EAV Concept Models
admin.site.register(exp_models.Descriptor)
admin.site.register(exp_models.DescriptorValue)
admin.site.register(exp_models.DescriptorNameValue)


class DescriptorMapAdmin(admin.ModelAdmin):
    model = exp_models.DescriptorMap
    list_display = ('descriptor_name_value', 'content_type', 'object_id', 'object')
    readonly_fields = ('object', )

admin.site.register(exp_models.DescriptorMap, DescriptorMapAdmin)


#         --------------Inlines------------
class DescriptorMapInline(GenericTabularInline):
    model = exp_models.DescriptorMap
    form = DescriptorMapInlineForm
    classes = ['extrapretty']
    extra = 1


class SampleInline(admin.StackedInline):
    model = exp_models.Sample
    classes = ['wide', 'collapse', 'extrapretty']
    extra = 0
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


@admin.register(exp_models.Sample)
class SampleAdmin(admin.ModelAdmin):
    model = exp_models.Sample
    inlines = [DescriptorMapInline] 

class ExperimentFileInline(admin.TabularInline):
    model = exp_models.ExperimentFile
    classes = ['extrapretty', 'wide']
    extra = 1

class ExperimentAdmin(admin.ModelAdmin):
    model = exp_models.Experiment
    inlines = [SampleInline, ExperimentFileInline]
    exclude = ['conditions', ]
    fieldsets = (
        ('Metadata', {
                'classes': ['wide'],
                'fields': ['users', 'project', 'platform', 'organism', 'prep_method']
            }
        ),
        
    )
admin.site.register(exp_models.Experiment, ExperimentAdmin)