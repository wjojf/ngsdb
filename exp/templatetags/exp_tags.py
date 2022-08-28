from django.utils.safestring import mark_safe
from django.template import Library, Node, TemplateSyntaxError, Variable

from exp.models import DescriptorMap

register = Library()



