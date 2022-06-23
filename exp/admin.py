from django.contrib import admin
from exp import models as exp_models

# Register your models here.
admin.site.register(exp_models.Experiment)
admin.site.register(exp_models.Project)
admin.site.register(exp_models.PrepMethod)

admin.site.register(exp_models.Descriptor)
admin.site.register(exp_models.DescriptorValue)
admin.site.register(exp_models.DescriptorMap)
admin.site.register(exp_models.ModelOrganism)


admin.site.register(exp_models.ExpPlatform)

