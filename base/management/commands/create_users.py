"""Management command to create initial users for the inventory system."""

from django.core.management.base import BaseCommand
from base.models import User


class Command(BaseCommand):
    help = 'Creates the 4 fixed users: 1 accountant and 3 representatives'

    def add_arguments(self, parser):
        parser.add_argument(
            '--password',
            type=str,
            default='inventory123',
            help='Password for all users (default: inventory123)'
        )

    def handle(self, *args, **options):
        password = options['password']
        
        # Check if users already exist
        if User.objects.filter(user_type__in=['accountant', 'representative']).exists():
            self.stdout.write(
                self.style.WARNING('Users already exist. Use --force to recreate.')
            )
            return
        
        # Create accountant
        accountant = User.objects.create_user(
            username='accountant',
            password=password,
            user_type='accountant',
            first_name='المحاسب',
            last_name='',
            phone='',
            address=''
        )
        self.stdout.write(
            self.style.SUCCESS(f'Created accountant: {accountant.username}')
        )
        
        # Create 3 representatives
        for i in range(1, 4):
            rep = User.objects.create_user(
                username=f'rep{i}',
                password=password,
                user_type='representative',
                first_name=f'مندوب {i}',
                last_name='',
                phone='',
                address=''
            )
            self.stdout.write(
                self.style.SUCCESS(f'Created representative: {rep.username}')
            )
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Created 4 users with password: {password}'
        ))
        self.stdout.write(self.style.WARNING(
            '⚠️  Please change passwords after first login!'
        ))
