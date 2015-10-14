from IPython.parallel.apps.launcher import HTCondorControllerLauncher
from django.shortcuts import render

from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import  Paginator, EmptyPage, PageNotAnInteger
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

	bm.save()

	tags = models.get_tags(models.split_title_on_tags(bm.title))
	for tag in tags:
		bm_tag = models.BookmarkTag()
		bm_tag.tag = tag
		bm_tag.bookmark = bm
		bm_tag.save()

	return HttpResponse()


@csrf_exempt
@printRequest
def handle_delete_bookmark(request):
	delete = request.DELETE
	bm_id = delete.get('bookmark_id')
	user_id = delete.get('user_id')

	bookmark = models.Bookmark.get(id=bm_id)[0]
	if user_id == bookmark.user_id:
		bookmark.delete()
		bookmark.save()
		return HttpResponse()
	else:
		return HttpResponseBadRequest()


@csrf_exempt
@printRequest
def handle_change_bookmark(request):
	post = request.POST

	id = post.get('bookmark_id')
	bm = models.Bookmark.objects.get(id=id)[0]
	if bm.user_id != post.get('user_id'):
		return HttpResponseBadRequest()

	bm.is_public = post.get('is_public')
	bm.description = post.get('description')
	bm.title = post.get('title')
	bm.save()

	#TODO: delete all old tags

	tags = models.get_tags(models.split_title_on_tags(bm.title))
	for tag in tags:
		bm_tag = models.BookmarkTag()
		bm_tag.tag = tag
		bm_tag.bookmark = bm
		bm_tag.save()

	return HttpResponse()


@printRequest
def handle_search_bookmarks(request):
	get = request.GET
	user_id = get.get('user_id')
	query = get.get('query')
	raw_tags = models.split_title_on_tags(query)
	tags = map(lambda x: models.find_tag(x), raw_tags)
	flag = True
	for x in tags:
		if x is None:
			# TODO: answer json
			return HttpResponse()

	objects = models.BookmarkTag.objects.filter(tag__in=tags).annotate(num=Count('bookmark'))
	ans = []
	for obj in objects:
		if obj.num < len(tags):
			continue
		ans.append(obj.bookmark)

	return ans


@printRequest
def handle_get_user_bookmarks(request):
	get = request.GET
	bookmarks_user_id = int(get.get('bookmarks_user_id'))
	user_id = int(get.get('user_id'))
	items_per_page = get.get('per_page')
	page = int(get.get('page'))

	bm_list = None
	try:
		bm_list = models.Bookmark.objects.filter(is_public=(bookmarks_user_id==user_id), user_id=bookmarks_user_id)
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

	result = [x.json() for x in result.object_list]
	data = {'objects': result, 'pages': pages_count, 'cur_page': page}
	data = json.dumps(data)

	return HttpResponse(data)


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

