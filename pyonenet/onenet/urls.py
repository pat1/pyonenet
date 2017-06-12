from django.conf.urls.defaults import *
#from django.contrib import admin

#from models import Program, Schedule

urlpatterns = patterns('pyonenet.onenet.views',
     (r'^$', 'masters'),
     (r'^master/(?P<id>\d)/$', 'master'),
     (r'^client/(?P<id>\d)/$', 'client'),
     (r'^masters/$', 'masters'),
     (r'^clients/$', 'clients'),
#     (r'^login/$', 'login'),
)

#urlpatterns += patterns('',
#     (r'^login/$', 'django.contrib.auth.views.login',{'template_name': 'onenet/login.html',}),
#)
