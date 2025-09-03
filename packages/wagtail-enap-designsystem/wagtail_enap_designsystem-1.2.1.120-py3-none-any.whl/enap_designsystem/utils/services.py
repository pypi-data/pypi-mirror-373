# utils/services.py
from django.core.mail import send_mail, get_connection, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class SimpleEmailService:
    """Serviço de email usando templates existentes"""
    
    @staticmethod
    def send_user_confirmation(user_email, user_name, form_title, form_data, submission_date):
        """Envia confirmação usando template forms/email_confirmation.html"""
        try:
            subject = f"Confirmação de Inscrição - {form_title}"
            
            # Contexto para o template
            context = {
                'user_name': user_name,
                'form_title': form_title,
                'submit_date': submission_date,  # seu template usa submit_date
                'form_data': form_data,
                'form_data_html': SimpleEmailService._format_data_table_html(form_data),
                'form_data_text': SimpleEmailService._format_data_text(form_data),
            }
            
            try:
                # Usar template
                html_content = render_to_string('forms/email_confirmation.html', context)
                text_content = strip_tags(html_content)
                
                # Criar email
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@enap.gov.br'),
                    to=[user_email],
                    connection = get_connection(
                        backend='django.core.mail.backends.smtp.EmailBackend',
                        host='10.224.4.40',
                        port=25,
                        use_tls=False,
                        use_ssl=False
                    ),
                )
                email.attach_alternative(html_content, "text/html")
                email.send()
                
                logger.info(f"✅ Email enviado para {user_email}")
                return True
                
            except Exception as template_error:
                logger.error(f"❌ Erro no template: {template_error}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Erro geral: {str(e)}")
            return False
    
    @staticmethod
    def send_admin_notification(admin_email, user_name, user_email, form_title, form_data, submission_date, user_ip=None):
        """Envia notificação para admin"""
        try:
            subject = f"Nova submissão: {form_title}"
            
            message = f"""
🔔 NOVA SUBMISSÃO DE FORMULÁRIO

📋 Formulário: {form_title}
📅 Data/Hora: {submission_date}
👤 Usuário: {user_name}
📧 Email: {user_email}
🌐 IP: {user_ip or 'Não disponível'}

📝 DADOS:
{SimpleEmailService._format_data_text(form_data)}

---
Sistema ENAP
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@enap.gov.br'),
                recipient_list=[admin_email],
                fail_silently=False,
            )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro admin: {str(e)}")
            return False
    
    @staticmethod
    def _format_data_text(form_data):
        """Formata dados para texto"""
        if not form_data:
            return "• Nenhum dado preenchido."
        
        formatted = []
        for field_id, value in form_data.items():
            if isinstance(value, list):
                value = ', '.join(str(v) for v in value)
            
            label = SimpleEmailService._get_field_label(field_id)
            formatted.append(f"• {label}: {value}")
        
        return '\n'.join(formatted)
    
    @staticmethod
    def _format_data_table_html(form_data):
        """Formata dados como tabela HTML"""
        if not form_data:
            return "<p style='text-align: center; color: #666;'>Nenhum dado foi preenchido.</p>"
        
        rows = []
        for field_id, value in form_data.items():
            if isinstance(value, list):
                value = ', '.join(str(v) for v in value)
            
            label = SimpleEmailService._get_field_label(field_id)
            rows.append(f"""
                <tr>
                    <td style="padding: 12px 15px; border-bottom: 1px solid #dee2e6; font-weight: 600;">{label}</td>
                    <td style="padding: 12px 15px; border-bottom: 1px solid #dee2e6;">{value}</td>
                </tr>
            """)
        
        return f"""
        <table class="data-table">
            <thead>
                <tr>
                    <th>Campo</th>
                    <th>Valor</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        """
    
    @staticmethod
    def _get_field_label(field_id):
        """Labels amigáveis"""
        labels = {
            'text_field': 'Nome',
            'email_field': 'Email', 
            'phone_field': 'Telefone',
            'cpf_field': 'CPF',
            'textarea_field': 'Comentários',
            'dropdown_field': 'Seleção',
            'radio_field': 'Opção',
            'checkbox_multiple_field': 'Seleções',
            'rating_field': 'Avaliação',
            'date_field': 'Data',
        }
        
        field_type = field_id.split('_field')[0] + '_field' if '_field' in field_id else field_id
        return labels.get(field_type, field_id.replace('_', ' ').title())
