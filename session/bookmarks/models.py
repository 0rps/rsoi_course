from django.db import models

import json
import hashlib
from datetime import datetime, timedelta
from decimal import Decimal


def exact(str):
	return r'\b' + str + r'\b'


class User(models.Model):
	name = models.CharField(max_length=32)
	last_name = models.CharField(max_length=32)
	email = models.EmailField()
	password = models.CharField(max_length=32)

	def json(self):
		dict = {}
		dict["name"] = self.name
		dict["last_name"] = self.last_name
		dict["email"] = self.email

		return json.dumps(dict)


def get_user_via_id(user_id):
	result = User.objects.get(id=int(user_id))
	return result


def get_user_via_email(email):
	result = User.objects.filter(email__iregex=exact(email))
	return result[0] if len(result) > 0 else None


class Cookie(models.Model):
	userId = models.IntegerField()
	token = models.CharField(max_length=64)
	lastTime = models.DateTimeField()

	def refresh(self):
		self.lastTime = datetime.now()
		self.save()


def generate_cookie(user_id):
	cookie = Cookie()
	cookie.userId = user_id
	cookie.lastTime = datetime.now()
	str_id = str(user_id)
	msc = str(datetime.now().microsecond)
	cookie.token = hashlib.md5(str_id + msc).hexdigest()
	cookie.save()
	return cookie


def get_cookie(cookie_id, token):
	cookie_list = Cookie.objects.filter(id=Decimal(cookie_id))
	if len(cookie_list) > 0 and cookie_list[0].token == token:
		cookie = cookie_list[0]
		if datetime.now() - cookie.lastTime < timedelta(hours=2):
			cookie.refresh()
			return cookie

	return None
