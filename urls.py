from django.conf.urls import patterns, include, url

from .views import httphandler_init_datastore

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'opengoldtwbot.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),


    url(r'gae/db_init/$', httphandler_init_datastore),
    
)
