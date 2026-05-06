from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tedapp.models import UserProfile


class Command(BaseCommand):
    help = 'Set user as owner'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to set as owner')

    def handle(self, *args, **options):
        username = options['username']
        try:
            user = User.objects.get(username=username)
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.role = 'owner'
            profile.save()
            self.stdout.write(self.style.SUCCESS(f'User {username} is now owner!'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User {username} not found'))