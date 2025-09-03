from django import template
import random

register = template.Library()

@register.filter
def mul(value, arg):
	try:
		return int(value) * int(arg)
	except:
		return ''

@register.filter
def classname(obj):
	return obj.__class__.__name__

@register.filter
def format_modalidade(value):
	if not value:
		return ""
	return value.replace("_", " ").capitalize()

@register.simple_tag
def random_default_image():
	return f"/static/enap_designsystem/icons/default_course_{random.randint(1, 8)}.png"
