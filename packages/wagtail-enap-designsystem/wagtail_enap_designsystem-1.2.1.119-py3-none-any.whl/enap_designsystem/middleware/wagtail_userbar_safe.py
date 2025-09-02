from django.utils.deprecation import MiddlewareMixin

class WagtailUserbarSafeMiddleware(MiddlewareMixin):
	def process_template_response(self, request, response):
		if hasattr(response, 'context_data') and response.context_data is not None:
			context = response.context_data
			page = context.get('page', None)

			# Garante que get_parent existe e é seguro chamar
			if (
				page and
				hasattr(page, 'get_parent') and
				callable(page.get_parent)
			):
				try:
					if not page.get_parent():
						context['show_wagtail_userbar'] = False
				except Exception:
					context['show_wagtail_userbar'] = False

		return response
