from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView
from gifts.models import Contact
from gifts.forms import UploadCSVForm
from django import forms

urlpatterns = patterns('gifts.views',
    url(r'^$', 'index', name = 'home'),
    url(r'^contacts/$', 'contacts', name = 'contacts'),
    url(r'^donations/$', 'donations', name = 'donations'),
    url(r'^contacts/(?P<contact_id>\d+)/', 
        'contact_record', name = 'contact_record'),
    url(r'^search/$', 'search', name = 'search'),
    url(r'^import/$', 'import_csv', name = 'import'),
)
