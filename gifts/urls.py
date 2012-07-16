from django.conf.urls import patterns, include, url

urlpatterns = patterns('gifts.views',
    url(r'^$', 'index', name = 'home'),
    url(r'^contacts/$', 'contacts', name = 'contacts'),
    url(r'^donations/$', 'donations', name = 'donations'),
    url(r'^asks/$', 'asks', name = 'asks'),
    url(r'^contacts/(?P<contact_id>\d+)/', 
        'contact_record', name = 'contact_record'),
    url(r'^asks/(?P<ask_id>\d+)/', 
        'ask_record', name = 'ask_record'),
    url(r'^search/$', 'search', name = 'search'),
    url(r'^import/$', 'import_csv', name = 'import'),
    url(r'^combine/$', 'combine', name = 'combine'),
)
