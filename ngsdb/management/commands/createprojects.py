from django.core.management.base import BaseCommand
from exp.models import Project

PROJECTS = [
    {'title': 'Test Project'},
    {'title': 'Another Project'},    
]


class Command(BaseCommand):
    help = 'Creates list of Experiment Projects from a given list'

    def handle(self, **options):
        for project_dict in PROJECTS:
            project_obj, created = Project.objects.get_or_create(
                title=project_dict['title']
            )
            if created:
                print(f'Project {project_obj} created!')
            project_obj.save()