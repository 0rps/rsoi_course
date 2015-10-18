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
		d["title"] = str(self.title)
		d["description"] = str(self.description)
		d["username"] = str(self.username)
		d["user_id"] = str(self.user_id)
		d["is_public"] = str(self.is_public)
		d["time"] = str(self.time)
		d["id"] = str(self.id)

		return d

	def short_json(self):
		d = {}
		d["title"] = str(self.title)
		d["username"] = str(self.username)
		d["user_id"] = str(self.user_id)
		d["is_public"] = str(self.is_public)
		d["time"] = str(self.time)
		d["id"] = str(self.id)

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
	result = Tag.objects.filter(name=tag)
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


