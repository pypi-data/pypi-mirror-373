"""
Management Command - Indexar páginas para o chatbot
"""

from django.core.management.base import BaseCommand
from enap_designsystem.services.chatbot_service import ChatbotService


class Command(BaseCommand):
    help = 'Indexa todas as páginas para o chatbot IA'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força reindexação de todas as páginas',
        )

    def handle(self, *args, **options):
        self.stdout.write('🚀 Iniciando indexação das páginas...')
        
        try:
            chatbot_service = ChatbotService()
            chatbot_service.indexar_todas_paginas()
            
            self.stdout.write(
                self.style.SUCCESS('✅ Indexação concluída com sucesso!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro durante a indexação: {e}')
            )