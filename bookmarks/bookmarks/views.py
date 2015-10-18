from IPython.parallel.apps.launcher import HTCondorControllerLauncher
from django.shortcuts import render

from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime
from django.db.models import Count

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
def handle_add_bookmark(request):

	put = request.REQUEST

	bm = models.Bookmark()
	bm.is_public = put.get('is_public')
	bm.description = put.get('description')
	bm.title = put.get('title')
	bm.user_id = put.get('user_id')
	bm.username = put.get('username')

	try:
		bm.save()
	except Exception as e:
		logerror(e.message)
		return HttpResponseBadRequest

	raw_tags = models.split_title_on_tags(bm.title)
	tags = models.get_tags(raw_tags)
	for tag in tags:
		bm_tag = models.BookmarkTag()
		bm_tag.tag = tag
		bm_tag.bookmark = bm
		bm_tag.save()

	loginfo("Bookmark added")
	return HttpResponse()


@csrf_exempt
@printRequest
def handle_remove_bookmark(request):
	delete = request.REQUEST
	bm_id = delete.get('bookmark_id')
	user_id = delete.get('user_id')

	if bm_id is None or user_id is None:
		logerror("Some params is NONE")
		return HttpResponseBadRequest

	bm_id = int(bm_id)
	user_id = int(user_id)

	bookmark = models.Bookmark.objects.get(pk=bm_id)
	tags = models.BookmarkTag.objects.filter(bookmark=bookmark)
	for tag in tags:
		tag.delete()

	if user_id == bookmark.user_id:
		bookmark.delete()
		return HttpResponse()
	else:
		return HttpResponseBadRequest()


@csrf_exempt
@printRequest
def handle_change_bookmark(request):
	post = request.POST

	id = post.get('bookmark_id')
	bm = models.Bookmark.objects.get(pk=int(id))
	if bm.user_id != int(post.get('user_id')):
		return HttpResponseBadRequest()

	bm.is_public = bool(post.get('is_public'))
	bm.description = post.get('description')
	bm.time = datetime.now()
	bm.save()

	return HttpResponse()


@printRequest
def handle_search_bookmarks(request):
	get = request.GET
	text = get.get('search_text')
	page = get.get('page')
	per_page = get.get('per_page')

	raw_tags = models.split_title_on_tags(text)
	tags = map(lambda x: models.find_tag(x), raw_tags)

	non_null_tags = []
	for x in tags:
		if x:
			non_null_tags.append(x)
	tags = non_null_tags

	if len(tags) == 0:
		data = {'cur_page': 1, 'pages': 1, 'objects':[]}
		return HttpResponse(json.dumps(data))

	objects = models.BookmarkTag.objects.filter(tag__in=tags)
	objects = objects.filter(bookmark__is_public=True)
	objects = objects.values('bookmark')
	objects = objects.annotate(num=Count('bookmark'))
	objects = objects.filter(num__gte=len(tags))
	objects = objects.order_by('bookmark__time')

	paginator = Paginator(objects, per_page)
	try:
		result = paginator.page(page)
	except PageNotAnInteger:
		page = 1
		result = paginator.page(page)
	except EmptyPage:
		page = paginator.num_pages
		result = paginator.page(paginator.num_pages)

	pages_count = paginator.num_pages

	objects=[]
	for x in result.object_list:
		bm = models.Bookmark.objects.get(pk=x['bookmark'])
		objects.append(bm.short_json())

	data = {'objects': objects, 'pages': pages_count, 'cur_page': page}
	data = json.dumps(data)

	return HttpResponse(data)


@printRequest
def handle_get_user_bookmarks(request):
	get = request.GET
	bookmarks_user_id = int(get.get('bookmarks_user_id'))
	user_id = int(get.get('user_id'))
	items_per_page = get.get('per_page')
	page = int(get.get('page'))

	bm_list = None
	try:
		if bookmarks_user_id == user_id:
			bm_list = models.Bookmark.objects.filter(user_id=bookmarks_user_id)
		else:
			bm_list = models.Bookmark.objects.filter(is_public=True, user_id=bookmarks_user_id)
	except Exception as e:
		logerror(e.message)
		return HttpResponseBadRequest()

	paginator = Paginator(bm_list, items_per_page)

	try:
		result = paginator.page(page)
	except PageNotAnInteger:
		page = 1
		result = paginator.page(page)
	except EmptyPage:
		page = paginator.num_pages
		result = paginator.page(paginator.num_pages)

	pages_count = paginator.num_pages

	result = [x.short_json() for x in result.object_list]
	data = {'objects': result, 'pages': pages_count, 'cur_page': page}
	data = json.dumps(data)

	return HttpResponse(data)

@printRequest
def handle_get_user_bookmark(request):
	get = request.GET
	id = get.get('bookmark_id')

	if id is None:
		logerror("Id is none")
		return HttpResponseBadRequest()

	try:
		bookmark = models.Bookmark.objects.get(pk=int(id))
	except Exception as e:
		logerror(e.message)
		return HttpResponseBadRequest

	loginfo("bookmark is found")

	return HttpResponse(json.dumps(bookmark.full_json()))


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