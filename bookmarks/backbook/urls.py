from django.conf.urls import patterns, include, url
from django.contrib import admin

from bookmarks import views

urlpatterns = patterns('', url(r'^bookmarks/?$', views.handle_get_user_bookmarks),)
