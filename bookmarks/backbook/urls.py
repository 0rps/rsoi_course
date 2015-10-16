from django.conf.urls import patterns, include, url
from django.contrib import admin

from bookmarks import views

urlpatterns = patterns('', url(r'^bookmarks/?$', views.handle_get_user_bookmarks),
					   url(r'^addbookmark/?$', views.handle_add_bookmark),
					   url(r'^changebookmark/?$', views.handle_change_bookmark),
					   url(r'^removebookmark/?$', views.handle_remove_bookmark),)
