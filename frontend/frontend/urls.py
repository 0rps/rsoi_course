from django.conf.urls import patterns, include, url
from bookmarks import session_views as sview, bookmarks_views as bview, news_views as nview, views


urlpatterns = patterns('',
    url(r'^/?$', views.index),
    url(r'^index/?$', views.index),
    url(r'^me/?$', sview.me),
    url(r'^bookmark/?$', bview.get_bookmark),
    url(r'^bookmarks/?$', bview.get_my_bookmarks),
    url(r'^userbookmarks/?$', bview.get_user_bookmarks),
    url(r'^search/?$', bview.search_bookmarks),
    url(r'^user/?$', sview.user_profile),
    url(r'^addbookmark/?$', bview.add_bookmark),
    url(r'^removebookmark/?$', bview.remove_bookmark),
    url(r'^changebookmark/?$', bview.change_bookmark),
    url(r'^login/?$', sview.login),
    url(r'^logout/?$', sview.logout),
    url(r'^register/?$', sview.register),
    url(r'^subscribe/?$', nview.subscribe),
    url(r'^unsubscribe/?$', nview.unsubscribe),
    url(r'^newsowners/?$', nview.get_news_owners),
    url(r'^news/?$',nview.get_news),)
