from django.shortcuts import render

from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

import json

from bookmarks import models
from log import logerror, loginfo


def printRequest(func):
	def wrapper(r, *args, **kwargs):
		loginfo(r.method + " " + r.get_full_path())
		return func(r, *args, **kwargs)

	return wrapper


@csrf_exempt
@printRequest
def handleRegisterRequest(request):

	put = request.REQUEST

	user = models.User()
	user.name = put.get('name')
	user.email = put.get('email')
	user.password = put.get('password')
	user.last_name = put.get('last_name')

	loginfo("register: " + "email " + user.email)

	if models.get_user_via_email(user.email):
		logerror("user with this email is existing")
		return HttpResponseBadRequest()
	user.save()
	loginfo("user registered")
	return HttpResponse()


@printRequest
def handleCheckCookieRequest(request):
	get = request.GET
	token = get.get('token')
	sessionId = get.get('id')

	cookie = models.get_cookie(sessionId, token)
	if cookie:
		loginfo('valid cookie')
		return HttpResponse(json.dumps({'userId': cookie.userId}))
	else:
		loginfo('invalid cookie')
		return HttpResponseBadRequest()


@csrf_exempt
@printRequest
def handleLoginRequest(request):
	# loginfo(request.get_full_path())
	post = request.POST

	email = post.get('email')
	password = post.get('password')

	loginfo("login request")
	loginfo("email: " + email)

	user = models.get_user_via_email(email)
	if user is None:
		loginfo("user is none")

	result = {}
	if user and user.password == password:
		cookie = models.generate_cookie(user.id)
		loginfo(str(cookie.id))
		result['id'] = cookie.id
		result['token'] = cookie.token
		result['userId'] = cookie.userId
		loginfo('login successful: ')
		loginfo('id: ' + str(cookie.userId))
		loginfo('token: ' + cookie.token)
		return HttpResponse(json.dumps(result))
	else:
		logerror('login failed')
		return HttpResponseBadRequest()


@csrf_exempt
@printRequest
def handleLogoutRequest(request):
	delete = request.REQUEST

	token = delete.get('token')
	sessionId = delete.get('id')

	loginfo("clear cookie: ")
	loginfo("token: " + token)
	loginfo('id: ' + sessionId)

	cookie = models.get_cookie(sessionId, token)
	if cookie:
		cookie.delete()
		loginfo('cookie deleted')

	return HttpResponse()


@printRequest
def handleMeRequest(request):
	get = request.GET

	userId = get.get('userId')
	user = models.get_user_via_id(userId)

	loginfo('user email' + str(user.email))

	return HttpResponse(user.json())

@printRequest
def handle_user_request(request):
	get = request.GET

	userId = get.get('userId')
	user = models.get_user_via_id(userId)

	loginfo('user email' + str(user.email))

	return HttpResponse(user.json())