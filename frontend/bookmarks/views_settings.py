__author__ = 'orps'

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.http import HttpResponseServerError
from django.http import HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

import requests

from bookmarks import forms
from bookmarks.log import loginfo, logerror
# Create your views here.

sessionServer = "http://127.0.0.1:8002"
backendNews = "http://127.0.0.1:8003"
backendBookmarks = "http://127.0.0.1:8005"
frontendServer = "http://127.0.0.1:8000"


def sessionWrapper(func):
	def wrapper(request, *args, **kwargs):
		cookie = request.COOKIES
		id = cookie.get('id')
		token = cookie.get('token')
		if id is not None and token is not None:
			response = requests.get(sessionServer + "/check?id=" + id + "&token=" + token)
			if response.status_code == 200:
				session = response.json()
				session['id'] = id
				session['token'] = token
				return func(request, session=session, *args, **kwargs)
		loginfo("session is None")
		return func(request, *args, **kwargs)

	return wrapper

def printRequest(func):
	def wrapper(r, *args, **kwargs):
		loginfo(r.method + " " + r.get_full_path())
		return func(r, *args, **kwargs)
	return wrapper

def authorizationRequired(func):
	def wrapper(r, *args, **kwargs):
		session = kwargs.get('session')
		if session is None:
			logerror("authorization failed")
			return HttpResponseRedirect(frontendServer + "/login")
		return func(r, *args, **kwargs)
	return wrapper