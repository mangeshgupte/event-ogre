from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'groups.views.home', name='home'),
    # url(r'^groups/', include('groups.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^polls/', include('polls.urls')),
    url(r'^events/', include('events.urls')),
    url(r'^accounts/', include('registration.backends.default.urls')),
    #url(r'', include('social_auth.urls')),
)

urlpatterns += staticfiles_urlpatterns()

