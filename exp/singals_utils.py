import os
from django.core.files.storage import default_storage
from django.db.models import FileField


def file_cleanup(sender, **kwargs):
    """
    File cleanup callback used to emulate the old delete
    behavior using signals. Initially django deleted linked
    files when an object containing a File/ImageField was deleted.

    Usage:
    >>> from django.db.models.signals import post_delete
    >>> post_delete.connect(file_cleanup, sender=MyModel, dispatch_uid="mymodel.file_cleanup")
    """
    for fieldname in [f.name for f in sender._meta.get_fields()]:
        try:
            field = sender._meta.get_field(fieldname)
        except:
            field = None

    if field and isinstance(field, FileField):
        inst = kwargs["instance"]
        f = getattr(inst, fieldname)
        m = inst.__class__._default_manager
        if (
            hasattr(f, "path")
            and os.path.exists(f.path)
            and not m.filter(
                **{"%s__exact" % fieldname: getattr(inst, fieldname)}
            ).exclude(pk=inst._get_pk_val())
        ):
            try:
                default_storage.delete(f.path)
            except:
                pass


def exp_directory_cleanup(sender, **kwargs):

    try:
        exp_directory_obj = kwargs['instance'].exp_directory
        exp_directory_obj.delete()
    except Exception as e:
        with open('debug.txt', 'a') as f:
            f.write(f'[ERROR] when deleting {kwargs["instance"]} -> {e}' + '\n')
        return 
