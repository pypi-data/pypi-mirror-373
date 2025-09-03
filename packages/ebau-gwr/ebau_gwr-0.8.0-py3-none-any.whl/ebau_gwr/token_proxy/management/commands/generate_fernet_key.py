from cryptography.fernet import Fernet
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Generate a fernet key for password encryption."

    def handle(self, *args, **options):
        key = Fernet.generate_key()
        self.stdout.write(key.decode())
