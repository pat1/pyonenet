from django.conf.urls import url
from pyonenet.onenet import views

#from django.contrib import admin

#from models import Program, Schedule

urlpatterns = [
     url(r'^$', views.masters),
     url(r'^master/(?P<id>\d)/$', views.master),
     url(r'^client/(?P<id>\d)/$', views.client),
     url(r'^masters/$', views.masters),
     url(r'^clients/$', views.clients),
#     url(r'^login/$', views.login),
]

#urlpatterns += patterns('',
#     (r'^login/$', 'django.contrib.auth.views.login',{'template_name': 'onenet/login.html',}),
#)
