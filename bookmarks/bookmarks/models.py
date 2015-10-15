from django.db import models

import json
import hashlib
from datetime import datetime, timedelta
from decimal import Decimal


def exact(str):
	return r'\b' + str + r'\b'


class Bookmark(models.Model):
	title = models.TextField()
	description = models.TextField()
	user_id = models.PositiveIntegerField()
	is_public = models.BooleanField(default=False)
	username = models.CharField(max_length=32)
	time = models.DateTimeField(default=datetime.now())

	def full_json(self):
		d = {}
		d["title"] = self.title
		d["description"] = self.description
		d["username"] = self.username
		d["user_id"] = self.user_id
		d["is_public"] = self.is_public
		d["time"] = self.time
		d["id"] = self.id

		return d

	def short_json(self):
		d = {}
		d["title"] = self.title
		d["username"] = self.username
		d["user_id"] = self.user_id
		d["is_public"] = self.is_public
		d["time"] = self.time
		d["id"] = self.id

		return d


class Tag(models.Model):
	name = models.CharField(max_length=64)


class BookmarkTag(models.Model):
	bookmark = models.ForeignKey(Bookmark)
	tag = models.ForeignKey(Tag)


def split_title_on_tags(title):
	result = filter(lambda x:  x.startswith('#'), title.split(" "))
	return map(lambda x: (x[1:]).lower(), result)


def find_tag(tag):
	result = Tag.objects().filter(name=tag)
	return result[0] if len(result) > 0 else None


def get_tags(str_tags):
	result = []
	for raw_tag in str_tags:
		tag = find_tag(raw_tag)
		if tag is None:
			tag = Tag()
			tag.name = raw_tag
			tag.save()

		result.append(tag)
	return result


def get_user_via_id(user_id):
	pass
	#result = User.objects.get(id=int(user_id))
	#return result
def get_user_via_email(email):
	pass
	#result = User.objects.filter(email=email)
	#return result[0] if len(result) > 0 else None
def generate_cookie(user_id):
	pass
	#cookie = Cookie()
	#cookie.userId = user_id
	#cookie.lastTime = datetime.now()
	#str_id = str(user_id)
	#msc = str(datetime.now().microsecond)
	#cookie.token = hashlib.md5(str_id + msc).hexdigest()
	#cookie.save()
	#return cookie
def get_cookie(cookie_id, token):
	pass
	#cookie_list = Cookie.objects.filter(id=Decimal(cookie_id))
	#if len(cookie_list) > 0 and cookie_list[0].token == token:
	#		cookie = cookie_list[0]
	#	dt = datetime.utcnow()
	#	dt_cookie = cookie.lastTime
	#	delta = dt - dt_cookie
	#	if delta < timedelta(hours=2):
	#		cookie.refresh()
	#		return cookie

	#return None
