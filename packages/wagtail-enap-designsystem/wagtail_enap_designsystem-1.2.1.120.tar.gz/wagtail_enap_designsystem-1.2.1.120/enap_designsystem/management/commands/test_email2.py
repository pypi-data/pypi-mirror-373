# home/management/commands/test_email.py
from django.core.management.base import BaseCommand
from django.core.mail import get_connection, EmailMessage

class Command(BaseCommand):
    connection = get_connection(
        backend='django.core.mail.backends.smtp.EmailBackend',
        host='10.224.4.40',
        port=25,
        use_tls=False,
        use_ssl=False
    ) 
    email = EmailMessage(
        subject='✅ Django SMTP Forçado - Deve Chegar!',
        body='Este email usa SMTP direto no Django, igual ao smtplib que funcionou!',
        from_email='noreply@enap.gov.br',
        to=['thaispaivacaliandra@gmail.com'],
        connection=connection
    )
    result = email.send() 
    print(f"✅ Email Django SMTP enviado: {result}")