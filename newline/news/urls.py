from django.conf.urls import patterns, include, url
from django.contrib import admin

from bookmarks import views

urlpatterns = patterns('',
					   url(r'^news/?$', views.get_news),
					   url(r'^subscribe/?$', views.subscribe),
					   url(r'^unsubscribe/?$', views.unsubscribe),
					   url(r'^issubscribed/?$', views.is_subscribed),
					   url(r'^newsownerslist/?$', views.get_newsowners_list),
					   url(r'^add/?$', views.add_bookmark),
					   url(r'^remove/?$', views.remove_bookmark),)
