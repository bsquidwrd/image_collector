"""webapps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.views.generic.base import TemplateView
from django.conf import settings
from django.contrib import admin
from django.views import static

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^media/(?P<path>.*)$', static.serve, {'document_root': settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', static.serve, {'document_root': settings.STATICFILES_DIR}),
    url(r'^humans.txt$', TemplateView.as_view(template_name='humans.txt', content_type='text/plain'), name='humans'),
    url(r'^', include('image_collector.urls', namespace='ic')),
]
