from attr import has
from django import template
from django.apps import apps
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.utils.safestring import mark_safe
from django.utils.encoding import smart_str
from django.template import Context
from django.template.defaultfilters import date, escape, capfirst
from django.contrib.auth.models import User
from django.db.models import Q

from exp.models import DescriptorMap, Sample

from nlib.views import ALLOWED_LOOKUP_TYPES


register = template.Library()


@register.simple_tag(takes_context=True)
def render_obj_users(context, obj, tag='p'):
    return mark_safe(f"<{tag}>{', '.join([str(user) for user in obj.users.all()])}</{tag}>")


@register.simple_tag(takes_context=True)
def render_obj(context, obj, css_class='order-fieldset', tag='p'):
    
    def get_fieldset(o, f:str):
        field = o._meta.get_field(f)
        
        try:
            fvalue = getattr(o, f)
        except:
            return ''
        
        custom_fields_string = ""
        tag_template = '{fn}:<strong>{fv} {cf}</strong>'

        # skip empty values or id field or filepath/users field
        if not fvalue or f == 'id' or 'filepath' in f or f == 'users':
            return ''
        
        # Render fields with custom_fields attr(ModelOrganism f.e)
        if hasattr(fvalue, 'custom_fields'):  
            if bool(fvalue.custom_fields.all()):
                descriptors_strings = [str(cf) for cf in fvalue.custom_fields.all()]
                custom_fields_string = ": " + ', '.join(descriptors_strings)
            
        return tag_template.format(
            fn=field.verbose_name, fv=fvalue, cf=custom_fields_string)
    
    
    def get_samples_fieldset(samples_queryset):
        
        if not bool(samples_queryset):
            return ''
        
        output = '<table>'
        
        # Add Column Names
        output += '<tr><th>Sample ID</th><th>Condition 1</th><th>Condition 2</th></tr>'
        
        for sample_obj in samples_queryset:
            sample_value = sample_obj.sample_value
            sample_descriptors = [str(desc_map.descriptor_name_value.desc_value) for desc_map in sample_obj.conditions.all()]
            tr_tag = '<tr>'
            
            for td in (sample_value, *sample_descriptors):
                tr_tag += f'<td>{td}</td>' 
            
            tr_tag += '</tr>'
            output += tr_tag
            
        output += '</table>'
        return output        
        
                    
    tpl = '<{tag} class="{css_class}">{fieldset}</{tag}>'
    fields = obj._meta.get_fields()
    lines = [tpl.format(
        tag=tag, 
        css_class=css_class,
        fieldset=get_fieldset(obj, f.name)) for f in fields
    ]
    
    # Handle Sample fields
    
    samples = obj.sample_set.all()
    lines.append(get_samples_fieldset(samples))
    
    return mark_safe(''.join(lines))


@register.inclusion_tag('includes/submit-row.html', takes_context=True)
def submit_row(context):
    buttons = []
    if 'submit_line' not in context:
        return {}
    submit_line = context['submit_line']
    if isinstance(submit_line, dict):
        submit_line = [submit_line,]
    for btn_dict in submit_line:
        btn_opts = {}
        tag = btn_dict.pop('tag', 'button')
        name = btn_dict.get('name', '')
        btn_opts['tag'] = tag 
        btn_opts['attrs'] = {'class': 'btn',}
        for k,v in btn_dict.items():
            if k in btn_opts['attrs']:
                btn_opts['attrs'][k] += ' {}'.format(v)
            else:
                btn_opts['attrs'][k] = v
        btn_opts['text'] = capfirst(name.replace('_', ' '))
        if tag == 'button':
            btn_opts['attrs']['name'] = '_{}'.format(name)
            btn_opts['attrs']['value'] = btn_opts['text']
            btn_opts['attrs']['type'] = 'submit'
        buttons.append(btn_opts)
    return {'buttons': buttons,}
    

@register.simple_tag()
def render_button(tag, text, **kwargs):
    '''
    Simple tag to render a button in bootstrap 3 style.
    Example:

        {% button button 'Add new item' class='btn btn-info' %}
    
    or using <a> tag:
        {% url 'add_new_item_view' as target_url %}
        {% render_button a 'Add new item' class='btn btn-info' href=target_url %}
    '''

    btn_tpl = '<{tag}{attrs}>{text}</{tag}>'
    if tag == 'button':
        if not 'name' in kwargs:
            kwargs['name'] = text.lower().replace(' ', '_')
        kwargs['value'] = '_{}'.format(kwargs['name'])
    attrs = []
    for k,v in kwargs.items():
        if isinstance(v, list):
            v = ' '.join(v)
        attrs.append('{0}="{1}"'.format(k, v))
    if attrs:
        attrs_flat = ' {}'.format(' '.join(attrs))
    return mark_safe(btn_tpl.format(tag=tag, text=text, attrs=attrs_flat))


@register.simple_tag()
def form_enc(form):
    from django.forms.fields import FileField
    res = ''
    for k, v in form.fields.items():
        if isinstance(v, FileField):
            res = 'enctype="multipart/form-data"'
            break
    return res


@register.simple_tag(takes_context=True)
def get_objects_by_user(context, user):
    object_list = context['object_list']
    return object_list.filter(user=user)


class RenderInputNode(template.Node):
    def __init__(self, input_type, name, value):
        self.input_type = input_type
        self.name = name
        self.value = template.Variable(value)
        self._value = value

    def render(self, context):
        t = '<input type="%s" name="%s" value="%s">'
        try:
            value = self.value.resolve(context)
        except template.VariableDoesNotExists:
            value = self._value
        return t % (self.input_type, self.name, value)


@register.tag(name='render_input')
def do_render_input(parser, token):
    '''
    Outputs HTML <input> tag with specified type, name, and value
    attributes.

    Usage:
            {% render_input [type] [name] "[value]"

    Example:
            {% render_input checkbox delete order.id %}
    or
            {% render_input button save_btn "Save and place an order" %}
    '''

    try:
        tag_name, input_type, name, value = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('%r tag requires exactly three arguments' % tag_name)
    return RenderInputNode(input_type, name, value)


@register.simple_tag()
def list_filter(field, klass, *args, **kwargs):
    '''
    Outputs list of filters:

            {% list_filter storage__location strains.Storage lookup_type=iexact rel=location tag=ul max_number=100 %}

    will produce (obj is the Storage instance being iterated on)

            <li><a href="?storage_location__iexact=obj.rel">obj.rel</a></li>
    '''
    tag = kwargs.get('tag', 'ul') # Tag to wrap the output in the template
    max_number = kwargs.get('max_number', None)
    lookup_type = kwargs.get('lookup_type', '') # ORM lookup type
    rel = kwargs.get('rel', 'pk')

    if tag in ('ul', 'ol'):
        t = '<li>%s</li>'
    elif tag == 'table':
        t = '<tr><th>%s</th><tr>'
    else:
        t = '<p>%s</p>'

    model = apps.get_model(*klass.split('.'))
    if model is None:
        raise template.TemplateSyntaxError('list_filter tag was given \
                an invalid model: %s' % model)

    if lookup_type and (rel != 'pk'):
        lookup_str = '%s__%s' % (field, lookup_type)
    else:
        lookup_str = field

    if max_number:
        qs = model.objects.all()[:max_number]
    else:
        qs = model.objects.all()
    result = []
    for obj in qs:
        try:
            val = smart_str(getattr(obj, rel))
        except AttributeError:
            val = ''
        s = '<a href="?%s=%s">%s</a>' % (lookup_str, val, val)
        result.append(t % s)
    return mark_safe(''.join(result))


@register.filter
def edit_link(obj):
    edit_link = obj.get_absolute_url().split('/')
    edit_link.insert(-2, 'edit')
    return '/'.join(edit_link)


@register.filter
def get_month(date):
    return date.strftime('%m')


@register.filter
def get_day(date):
    return date.strftime('%d')


@register.filter
def get_str_year(date):
    return date.strftime('%Y')

@register.filter(name='render_dict')
def render_dict(value, tag='li'):
    tmpl = '<%s>%s: %s</%s>'
    res = []
    if not isinstance(value, dict):
        return ''
    for lookup, val in value.items():
        bits = lookup.split('__')
        if bits[-1] in ALLOWED_LOOKUP_TYPES:
            field = ' '.join(bits[:-1])
        else:
            field = ' '.join(bits[:-1])
        if val:
            res.append(tmpl % (tag, field, val, tag))
    return mark_safe(''.join(res))


@register.filter(name='add_css')
def add_css(field, css):
    return field.as_widget(attrs={'class': css})


@register.simple_tag(takes_context=True)
def render_tabs(context):
    lines = []
    tab_item_tpl = '<li{css}><a href="{url}">{text}</a></li>'
    for tab_text,link_params in context['tabs'].items():
        link_url,is_active = link_params
        if is_active:
            css = ' class="active"'
            url = '#'
        else:
            css = ''
            url = link_url
        lines.append(tab_item_tpl.format(
            css=css,
            url=url,
            text=tab_text)
            )
    return mark_safe(''.join(lines))
