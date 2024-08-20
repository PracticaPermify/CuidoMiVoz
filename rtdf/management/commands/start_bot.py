from django.core.management.base import BaseCommand
from rtdf.bot_telegram import main as start_telegram_bot

class Command(BaseCommand):
    help = 'Inicia el bot de Telegram'

    def handle(self, *args, **kwargs):
        start_telegram_bot()