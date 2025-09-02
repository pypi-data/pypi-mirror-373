from django import template
from ..models import ConcursoInovacao

register = template.Library()

@register.simple_tag(takes_context=True)
def get_concurso_menu(context):
    """Pega o menu do concurso pai"""
    page = context.get('page')
    
    if page:
        # Se a página atual é um ConcursoInovacao
        if isinstance(page, ConcursoInovacao):
            return page.menu_navegacao
        
        # Se é uma página filha, pega o menu do pai
        parent = page.get_parent()
        while parent:
            if isinstance(parent.specific, ConcursoInovacao):
                return parent.specific.menu_navegacao
            parent = parent.get_parent()
    
    return None