from django.db import models, transaction, IntegrityError
from django.template.defaultfilters import slugify


class SluggedModel(models.Model):
    '''
    An abstract model that provides an automatic slug field.
    The slug field is created using one of the following fields: `title`,
    `name`, `caption` in that order.

    If none of these fields exists on the model, the slug is calculated
    using model's name and pk value.
    '''
    slug = models.SlugField(editable=False, blank=True)

    class Meta:
        abstract = True

    def _get_slug(self, i):
        fields = self._meta.get_all_field_names()
        if 'title' in fields:
            f = getattr(self, 'title')
        elif 'name' in fields:
            f = getattr(self, 'name')
        elif 'caption' in fields:
            f = getattr(self, 'caption')
        else:
            f = self._meta.verbose_name
        l = 49 - len(str(i))
        return '%s_%d' % (slugify(f)[:l], i)

    def save(self, *args, **kwargs):
        '''
        Sets unique slug before saving. Inspired by Alex Gaynor's
        django-taggit.
        '''

        if not self.pk and not self.slug:
            try:
                i = self._default_manager.all().order_by('pk')[0].pk
            except IndexError:
                i = 1
            self.slug = self._get_slug(i)
            while True:
                i += 1
                try:
                    sid = transaction.savepoint()
                    res = super(SluggedModel, self).save(*args, **kwargs)
                    transaction.savepoint_commit(sid)
                    return res
                except IntegrityError:
                    transaction.savepoint_rollback(sid)
                    self.slug = slef._get_slug(i)
        else:
            return super(SluggedModel, self).save(*args, **kwargs)


class TimestampedSluggedModel(SluggedModel):
    '''
    An abstract model that automatically provides `created`,
    `last_modified`, and `slug` fields.
    '''
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TimestampedModel(models.Model):
    '''
    An abstract model that provides `created` and `last_modified`
    fields "out of the box".
    '''
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
