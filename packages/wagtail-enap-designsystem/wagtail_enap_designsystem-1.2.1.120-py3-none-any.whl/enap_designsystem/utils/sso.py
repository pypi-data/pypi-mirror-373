import time
import requests
from django.conf import settings

def get_valid_access_token(session):
	aluno = session.get("aluno_sso")
	if not aluno:
		return None

	# Se ainda não expirou, retorna o token atual
	if aluno.get("access_token_expires_at", 0) > time.time():
		return aluno["access_token"]

	# Renovar usando o refresh_token
	refresh_token = aluno.get("refresh_token")
	if not refresh_token:
		return None

	data = {
		"grant_type": "refresh_token",
		"client_id": settings.SSO_CLIENT_ID,
		"client_secret": settings.SSO_CLIENT_SECRET,
		"refresh_token": refresh_token,
	}
	headers = {
		"Content-Type": "application/x-www-form-urlencoded"
	}

	verify_ssl = not settings.DEBUG

	response = requests.post(settings.SSO_TOKEN_URL, data=data, headers=headers, verify=verify_ssl)
	if response.status_code != 200:
		return None

	tokens = response.json()
	session["aluno_sso"]["access_token"] = tokens["access_token"]
	session["aluno_sso"]["refresh_token"] = tokens["refresh_token"]
	session["aluno_sso"]["access_token_expires_at"] = int(time.time()) + tokens.get("expires_in", 300)
	session.modified = True

	return tokens["access_token"]
