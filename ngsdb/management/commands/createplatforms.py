from django.core.management.base import BaseCommand
from exp.models import ExpPlatform


PLATFORMS = [
    {
        'title': '',
        'n_reads': 1,
        'length_libtype': ''
    }
]


class Command(BaseCommand):
    help = 'Creates a list of ExpPlatform objects from a given list'


    def handle(self, *args, **options):
        
        for platform_dict in PLATFORMS:
            platform_obj, created = ExpPlatform.objects.get_or_create(
                title=platform_dict['title'],
                n_reads=platform_dict['n_reads'],
                length_libtype=platform_dict['length_libtype']
            )
            if created:
                print(f'Platform {platform_obj} created!')
            platform_obj.save()
        