# enap_designsystem/context_processors.py

from django.conf import settings
from .models import EnapNavbarSnippet


def global_template_context(request):
	return {
		'debug': settings.DEBUG
	}




def navbar_context(request):
    """
    Adiciona EnapNavbarSnippet a todos os templates
    """
    try:
        navbar = EnapNavbarSnippet.objects.first()
        return {'enap_navbar': navbar}
    except EnapNavbarSnippet.DoesNotExist:
        return {'enap_navbar': None}