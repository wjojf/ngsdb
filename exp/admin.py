from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from exp import models as exp_models
from exp.forms import DescriptorMapInline

# Register your models here.
admin.site.register(exp_models.Experiment)

admin.site.register(exp_models.Project)
admin.site.register(exp_models.PrepMethod)

admin.site.register(exp_models.Descriptor)
admin.site.register(exp_models.DescriptorValue)
admin.site.register(exp_models.DescriptorMap)


class DescriptorMapInline(GenericTabularInline):
    model = exp_models.DescriptorMap
    form = DescriptorMapInline
    extra = 1

class ModelOrganismAdmin(admin.ModelAdmin):
    model = exp_models.ModelOrganism
    inlines = [DescriptorMapInline]


admin.site.register(exp_models.ModelOrganism, ModelOrganismAdmin)



admin.site.register(exp_models.ExpPlatform)

