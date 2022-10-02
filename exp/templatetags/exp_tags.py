from django.utils.safestring import mark_safe
from django.template import Library
from django.urls import reverse

from exp.models import ExperimentFile

register = Library()


@register.simple_tag(takes_context=True)
def plots_dropdown(context, obj):
    obj_files = ExperimentFile.objects.filter(experiment=obj)

    if not bool(obj_files):
        return mark_safe('')

    output = ['<li class="dropdown navbar-right">']
    
    title_href = '''<a href="" class="dropdown-toggle" data-toggle="dropdown">
                        Plots
                   </a>'''
    output.append(title_href)

    output.append('<ul class="dropdown-menu">')

    for obj_file in obj_files:
        li_template = '<li><a href={href}>{text}</a></li>'
        
        if obj_file.is_nextseq:
            continue
        elif obj_file.is_deseq:
            text = 'Volcano Plot'
        elif obj_file.is_count_matrix:
            text = 'PCA Plot'
        
        output.append(
            mark_safe(
                li_template.format(
                    href=obj_file.get_absolute_url(),
                    text=text
                )
            )
        )

    output.append('</ul>') 
    output.append('</li>')

    return mark_safe(''.join(output))
    