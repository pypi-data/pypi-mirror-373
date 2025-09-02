from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = get_user_model().objects.filter(is_superuser=True).first()
        if user:
            self.stdout.write(f'The superuser "{user.username}" already exists.')
        else:
            password = 'admin'
            user = get_user_model().objects.create_superuser('admin', 'admin@example.com', password)
            self.stdout.write(
                f"""A new superuser with the following data was created:
                login:    {user.username}
                email:    {user.email}
                password: {password}"""
            )
