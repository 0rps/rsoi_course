# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('bookmarks', '0003_auto_20151006_1844'),
    ]

    operations = [
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.TextField()),
                ('owner_id', models.IntegerField()),
                ('bookmark_id', models.IntegerField()),
                ('time', models.DateTimeField(default=datetime.datetime(2015, 10, 18, 15, 27, 41, 794684))),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Subscriber',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subscriber', models.IntegerField()),
                ('owner', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubscriberNews',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('record', models.ForeignKey(to='bookmarks.Record')),
                ('subscriber', models.ForeignKey(to='bookmarks.Subscriber')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.DeleteModel(
            name='Cookie',
        ),
        migrations.DeleteModel(
            name='User',
        ),
    ]
