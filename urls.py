from django.conf.urls import patterns, include, url
from bot import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'opengoldtwbot.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),


    url(r'gae/$', views.gold_passbook_digest_view, name='passbook_digest_view'),
    url(r'gae/passbook/(?P<p_yyyy>[-\w]+)/$', views.gold_passbook_year_view, name='passbook_year_view'),
    url(r'gae/db_init/$', views.httphandler_init_datastore, name='datastore_init'),
    url(r'gae/db_clean/$', views.gold_passbook_clean_view, name='datastore_clean'),
    url(r'gae/db_upate_task/$', views.httphandler_daily_update_chain_task, name='datastore_update_task'),
    url(r'gae/db_update_by_date/(?P<p_date_str>[-\w]+)/$', views.gold_passbook_update_by_date, name='datastore_update_by_date'),
    
    
)
