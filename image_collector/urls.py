# Project: image_collector
# File Name: urls
# Created by: bsquidwrd
# Created on: 4/1/2016


from django.conf.urls import url

from image_collector import views

urlpatterns = [
    url(r'^$', views.index_view, name='index'),
    url(r'^user$', views.users_view, name='users_view'),
    url(r'^user/(?P<username>\w+)$', views.user_view, name='user_view'),
    url(r'^site$', views.sites_view, name='sites_view'),
    url(r'^site/(?P<site>\w+)$', views.site_view, name='site_view'),
    url(r'^post/(?P<post_id>\w+)$', views.post_view, name='post_view'),
    url(r'^(?P<requested_image>.*)$', views.image_view, name='image_view'),
]
