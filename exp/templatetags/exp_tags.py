from django.utils.safestring import mark_safe
from django.template import Library

from exp.models import ExperimentFile

register = Library()

def generate_href_tag(url_name, id:int):
    return '{% ' + f'url {url_name} {id}' + '%}'


@register.simple_tag(takes_context=True)
def plots_dropdown(context, obj):
    obj_files = ExperimentFile.objects.filter(experiment=obj)

    if not bool(obj_files):
        return mark_safe('')

    output = ['<li class="dropdown">']
    
    title_href = '''<a href="" class="dropdown-toggle" data-toggle="dropdown">
                        Plots
                        <b class="caret"></b>
                   </a>'''
    output.append(title_href)

    output.append('<ul class="dropdown-menu">')

    for obj_file in obj_files:
        li_template = '<li><a href={href}>{text}</a></li>'
        
        if obj_file.is_deseq:
            output.append(
                mark_safe(
                    li_template.format(
                        href=f"{generate_href_tag('volacno-plot', obj_file.id)}",
                        text='Volcano Plot'
                    )
                )
            )
        elif obj_file.is_count_matrix:
            output.append(
                li_template.format(
                    href=generate_href_tag('pca-plot', obj_file.id),
                    text='PCA Plot'
                ) 
            )

    output.append('</ul>') 
    output.append('</li>')

    return mark_safe(''.join(output))
    