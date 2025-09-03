# home/management/commands/test_simple_email.py
from django.core.management.base import BaseCommand
from django.core.mail import send_mail, EmailMultiAlternatives

class Command(BaseCommand):
    help = 'Testa envio de email'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, required=True, help='Email para teste')

    def handle(self, *args, **options):
        email = options['email']
        
        self.stdout.write('🧪 TESTANDO EMAIL...')

        try:
            send_mail( 
                subject='Sua mensagem importante',
                message='Olá! Esta é sua mensagem.',
                from_email='noreply@enap.gov.br',
                recipient_list=['thaispaivacaliandra@gmail.com', 'moacir.kurmann@enap.gov.br', 'moacir@mck2.com.br'],
                fail_silently=False,
                html_message='<p>Olá! Esta <b>é</b> sua mensagem.</p>'
            )

            self.stdout.write(self.style.SUCCESS('✅ Email enviado!'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'💥 Erro: {str(e)}'))
