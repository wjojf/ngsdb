from django.core.management.base import BaseCommand
from django.contrib.auth.models import User 


DEFAULT_PASSWORD = '12345'
USERS = [
    {'username': 'testuser', 'password': DEFAULT_PASSWORD}
]

class Command(BaseCommand):
    help = 'Creates User objects from a given list'


    def handle(self, **options):
        
        for user_dict in USERS:
            user_obj, created = User.objects.get_or_create(
                username=user_dict['username'],
                password=user_dict['password']
            )
            print(f'User {user_obj} created')
            user_obj.save()
    