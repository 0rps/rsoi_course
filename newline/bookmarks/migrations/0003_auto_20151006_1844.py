# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('bookmarks', '0002_auto_20150301_1348'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='phone',
        ),
        migrations.AddField(
            model_name='cookie',
            name='lastTime',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 6, 18, 44, 23, 79663, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='last_name',
            field=models.CharField(default='', max_length=32),
            preserve_default=False,
        ),
    ]
