from django.conf.urls import patterns, include, url
from bookmarks import session_views as sview, bookmarks_views as bview, views


urlpatterns = patterns('',
    url(r'^/?$', views.index),
    url(r'^index/?$', views.index),
    url(r'^me/?$', sview.me),
    url(r'^bookmarks/?$', bview.get_my_bookmarks),
    url(r'^addbookmark/?$', bview.add_bookmark),
    url(r'^removebookmark/?$', bview.remove_bookmark),
    url(r'^login/?$', sview.login),
    url(r'^logout/?$', sview.logout),
    url(r'^register/?$', sview.register),
)
