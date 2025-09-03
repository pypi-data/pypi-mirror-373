# home/management/commands/test_simple_email.py
from django.core.management.base import BaseCommand
from enap_designsystem.utils.services import SimpleEmailService

class Command(BaseCommand):
    help = 'Testa envio de email'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, required=True, help='Email para teste')

    def handle(self, *args, **options):
        email = options['email']
        
        self.stdout.write('🧪 TESTANDO EMAIL...')
        
        test_data = {
            'text_field_123': 'João da Silva',
            'email_field_456': email,
            'phone_field_789': '(61) 99999-9999',
        }

        try:
            success = SimpleEmailService.send_user_confirmation(
                user_email=email,
                user_name='João da Silva',
                form_title='Teste ENAP',
                form_data=test_data,
                submission_date='26/06/2025 às 14:30'
            )

            if success:
                self.stdout.write(self.style.SUCCESS('✅ Email enviado!'))
            else:
                self.stdout.write(self.style.ERROR('❌ Erro ao enviar'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'💥 Erro: {str(e)}'))
