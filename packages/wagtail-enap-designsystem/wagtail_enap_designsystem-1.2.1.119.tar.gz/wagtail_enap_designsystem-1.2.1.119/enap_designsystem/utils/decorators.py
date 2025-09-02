from django.shortcuts import redirect
from functools import wraps

def aluno_login_required(view_func):
	@wraps(view_func)
	def wrapper(request, *args, **kwargs):
		if not request.session.get("aluno_sso"):
			return redirect("/")  # antes era: return redirect("/login-sso/")
		return view_func(request, *args, **kwargs)
	return wrapper