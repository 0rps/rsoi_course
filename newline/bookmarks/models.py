from django.db import models

import json
import hashlib
from datetime import datetime, timedelta
from decimal import Decimal


def exact(str):
	return r'\b' + str + r'\b'

class Subscriber(models.Model):
	subscriber = models.IntegerField()
	owner = models.IntegerField()


class Record(models.Model):
	title = models.TextField()
	owner_id = models.IntegerField()
	bookmark_id = models.IntegerField()
	time = models.DateTimeField(default=datetime.now())

	def json(self):
		d = {'title': str(self.title),
			 'owner_id': str(self.owner_id),
			 'bookmark_id': str(self.bookmark_id),
			 'time': str(self.time)}
		return d


class SubscriberNews(models.Model):
	subscriber = models.ForeignKey(Subscriber)
	record = models.ForeignKey(Record)