from django.shortcuts import render

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

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
def add_bookmark(request):

	par = request.REQUEST
	user_id = int(par.get('user_id'))
	bm_id = int(par.get('bookmark_id'))
	title = par.get('title')

	record = models.Record()
	record.bookmark_id = bm_id
	record.title = title
	record.owner_id = user_id
	record.save()

	loginfo("record created")

	subscribers = models.Subscriber.objects.filter(owner=user_id)
	for user in subscribers:
		link = models.SubscriberNews()
		link.record = record
		link.subscriber = user
		link.save()

	loginfo("news created")

	return HttpResponse()


@csrf_exempt
@printRequest
def remove_bookmark(request):
	par = request.REQUEST
	bm_id = int(par.get('bookmark_id'))

	try:
		record = models.Record.objects.filter(bookmark_id=bm_id)[0]
	except Exception as e:
		loginfo(e.message)
		return HttpResponse()

	news = models.SubscriberNews.objects.filter(record=record)
	for unit in news:
		unit.delete()

	record.delete()
	loginfo("success")
	return HttpResponse()


@printRequest
def is_subscribed(request):
	get = request.GET
	subscriber_id = int(get.get('subscriber'))
	owner_id = int(get.get('owner'))
	ans = local_is_subscribed(owner_id, subscriber_id)
	if ans:
		return HttpResponse(json.dumps({'subscribed': True}))
	else:
		return HttpResponse(json.dumps({'subscribed': False}))


@csrf_exempt
@printRequest
def subscribe(request):
	get = request.REQUEST
	subscriber_id = int(get.get('subscriber'))
	owner_id = int(get.get('owner'))
	ans = local_is_subscribed(owner_id, subscriber_id)

	if ans:
		loginfo("success")
		return HttpResponse()

	try:
		sbs = models.Subscriber()
		sbs.subscriber = subscriber_id
		sbs.owner = owner_id
		sbs.save()
	except Exception as e:
		logerror(e.message)
		return HttpResponseServerError

	records = models.Record.objects.filter(owner_id=owner_id)
	for record in records:
		news = models.SubscriberNews()
		news.record = record
		news.subscriber = sbs
		news.save()

	loginfo("success")
	return HttpResponse()

@csrf_exempt
@printRequest
def unsubscribe(request):
	get = request.REQUEST
	subscriber_id = int(get.get('subscriber'))
	owner_id = int(get.get('owner'))

	ans = local_is_subscribed(owner_id, subscriber_id)
	if ans:
		news = models.SubscriberNews.objects.filter(subscriber=ans)
		for ns in news:
			ns.delete()
		ans.delete()

	loginfo("success")
	return HttpResponse()


@printRequest
def get_news(request):
	get = request.GET
	page = int(get.get('page'))
	per_page = int(get.get('per_page'))
	subscriber = int(get.get('user_id'))

	objects = models.SubscriberNews.objects.filter(subscriber__subscriber=subscriber).order_by('record__time')
	paginator = Paginator(objects, per_page)

	try:
		result = paginator.page(page)
	except PageNotAnInteger:
		page = 1
		result = paginator.page(page)
	except EmptyPage:
		page = paginator.num_pages
		result = paginator.page(page)

	objects = result.object_list
	data = [x.record.json() for x in objects]
	objects = data

	data = {'objects': objects, 'page':page, 'count': paginator.num_pages}

	loginfo("success")
	return HttpResponse(json.dumps(data))


@printRequest
def get_newsowners_list(request):
	get = request.GET
	subscriber = get.get('user_id')
	owners = local_get_newsowners_list(subscriber)
	data = [str(x.owner) for x in owners]
	loginfo("success")
	return HttpResponse(json.dumps(data))


def local_get_newsowners_list(subscriber_id):
	subscriber_id = int(subscriber_id)
	owners = models.Subscriber.objects.filter(subscriber=subscriber_id)
	return owners

def local_is_subscribed(owner_id, subscriber_id):
	subscriber_id = int(subscriber_id)
	owner_id = int(owner_id)

	subscribers = models.Subscriber.objects.filter(owner=owner_id, subscriber=subscriber_id)
	if len(subscribers) > 0:
		return subscribers[0]
	else:
		return None
