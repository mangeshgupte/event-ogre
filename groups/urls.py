from django.contrib import admin
import allauth
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls import patterns, include, url

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'groups.views.home', name='home'),
    # url(r'^groups/', include('groups.foo.urls')),

    url(r'^accounts/', include('allauth.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^events/', include('events.urls')),
)

urlpatterns += staticfiles_urlpatterns()

