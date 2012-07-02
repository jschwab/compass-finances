from django.conf.urls import patterns, include, url
import django.contrib.auth.views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'finances.views.home', name='home'),
    url(r'^gifts/', include('gifts.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls), name = 'admin'),

    # manage login & logout
    url(r'^login/$', django.contrib.auth.views.login),
    url(r'^logout/$', django.contrib.auth.views.logout, name = 'logout'),
                       
)
