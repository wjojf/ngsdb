from django.core.management.base import BaseCommand
from exp.models import ExpPlatform, PrepMethod


PLATFORMS = [
    {
        'method': '',
        'kit': '',
    }
]


class Command(BaseCommand):
    help = 'Creates a list of ExpPlatform objects from a given list'

    def handle(self, **options):
        for platform_dict in PLATFORMS:
            platform_obj, created = ExpPlatform.objects.get_or_create(
                method=platform_dict['method'],
                kit = platform_dict['kit']
            )
            if created:
                print(f'Project {platform_obj} created!')
            platform_obj.save()