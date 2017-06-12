# Create your views here.

from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse,HttpResponseRedirect
import  django.contrib.auth

import pyonenet.pyonenet_config
import pyonenet.pyonenet_core
import pyonenet.settings

#from django.forms.extras.widgets import SelectDateWidget
from widgets import MySelectDateWidget

from pyonenet.onenet.models import Master as DBmaster 
from pyonenet.onenet.models import Client as DBclient 



##@login_required()
def master(request,id):

    return render_to_response('onenet/master.html', {'master': DBmaster.objects.filter(id=id),'media_url':pyonenet.settings.MEDIA_URL})

##@login_required()
def masters(request):

    return render_to_response('onenet/master.html', {'master': DBmaster.objects.all(),'media_url':pyonenet.settings.MEDIA_URL})

##@login_required()
def client(request,id):

    return render_to_response('onenet/client.html', {'client': DBclient.objects.filter(master__id__exact=id),'media_url':pyonenet.settings.MEDIA_URL})

def clients(request):

    return render_to_response('onenet/client.html', {'client': DBclient.objects.all(),'media_url':pyonenet.settings.MEDIA_URL})

#def login(request):
#    django.contrib.auth.views.login (request,template_name='onenet/login.html')
#
