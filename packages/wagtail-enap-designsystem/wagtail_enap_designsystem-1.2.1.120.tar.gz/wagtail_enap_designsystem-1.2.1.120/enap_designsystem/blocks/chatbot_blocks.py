"""
Blocks do Chatbot IA para Design System ENAP
"""

from wagtail.blocks import StructBlock, CharBlock, BooleanBlock
from wagtail.snippets.blocks import SnippetChooserBlock


class ChatbotBlock(StructBlock):
    """Block do chatbot para uso em páginas"""
    
    chatbot_widget = SnippetChooserBlock(
        'enap_designsystem.ChatbotWidget',
        label="Widget do Chatbot",
        help_text="Escolha a configuração visual do chatbot"
    )
    
    titulo_personalizado = CharBlock(
        required=False,
        help_text="Deixe vazio para usar o título do widget"
    )
    
    mostrar_apenas_nesta_pagina = BooleanBlock(
        required=False,
        default=False,
        help_text="Se marcado, só aparece nesta página específica"
    )
    
    desabilitar_chatbot_global = BooleanBlock(
        required=False,
        default=False,
        help_text="Se marcado, remove o chatbot global desta página"
    )

    class Meta:
        template = 'enap_designsystem/blocks/chatbot_block.html'
        icon = 'user'
        label = 'Chatbot IA'
        help_text = 'Adiciona o chatbot inteligente à página'