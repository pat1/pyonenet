from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy,ugettext
from django.utils import timezone

from django.db.models import permalink
#from pyonenet.tv.managers import EpisodeManager

import datetime, calendar, decimal
from django.core.exceptions import ValidationError

def validate_onoff(value):
    if value != 0 and value != 1 and not value is None:
        raise ValidationError(u'%s is not 0 or 1 (or None)' % value)

#def validate_name(value):
#    if len(value) != 3  and not (value is None):
#        raise ValidationError(u'%s deve essere di 3 cifre (or None)' % value)
#    try:
#        intvalue=int(value)
#    except:
#        raise ValidationError(u'%s deve essere numerico (or None)' % value)
#
#    if  intvalue < 100  and not (value is None):
#        raise ValidationError(u'%s deve essere di 3 cifre (or None)' % value)


import platform
if platform.system() == "Linux":
    DEVICE_CHOICES=(
        ("/dev/ttyUSB0","USB0"),
        ("/dev/ttyUSB1","USB1"),
        ("/dev/ttyUSB2","USB2"),
        ("/dev/ttyUSB3","USB3"),
        )
else:
    DEVICE_CHOICES=(
        ("COM1","COM1"),
        ("COM2","COM2"),
        ("COM3","COM3"),
        ("COM4","COM4"),
        )

REGION_CHOICES=(
	("EUR","Europa"),
	("US","United States"),
	)

CHANNEL_CHOICES=(
	("1","Channel 1"),
	("2","Channel 2"),
	("3","Channel 3"),
	("4","Channel 4"),
	("5","Channel 5"),
	("6","Channel 6"),
	("7","Channel 7"),
	("8","Channel 8"),
	("9","Channel 9"),
	("10","Channel 10"),
	("11","Channel 11"),
	("12","Channel 12"),
	("13","Channel 13"),
	("14","Channel 14"),
	("15","Channel 15"),
	("16","Channel 16"),
	("17","Channel 17"),
	("18","Channel 18"),
	("19","Channel 19"),
	("20","Channel 20"),
	("21","Channel 21"),
	("22","Channel 22"),
	("23","Channel 23"),
	("24","Channel 24"),
	("25","Channel 25"),
	)


PRIORITY_CODES = (
    (1, ugettext_lazy('Urgent')),
    (2, ugettext_lazy('Normal')),
    (3, ugettext_lazy('When possible')),
    )

PINSTATE_CHOICES=(
	("input","input pin"),
	("output","output pin"),
	("disable","disabled pin"),
	)

PROTOCOL_CHOICES=(
	("onenet","One-net"),
	("oneway","One-way"),
	("jsrpc" ,"JSON-rpc"),
	)

class Zone(models.Model):

    zone = models.CharField(ugettext_lazy('Zone'),max_length=40)

    def __unicode__(self):
        return self.zone

class Floor(models.Model):

    floor = models.CharField(ugettext_lazy('Floor'),max_length=40)

    def __unicode__(self):
        return self.floor

class Room(models.Model):

    room = models.CharField(ugettext_lazy('Room'),max_length=40)

    def __unicode__(self):
        return self.room


class Master(models.Model):

	name = models.CharField(ugettext_lazy("Name"),max_length=50,unique=True,editable=True)
	device = models.CharField(ugettext_lazy("Serial device"),max_length=50,unique=True,choices=DEVICE_CHOICES,editable=True)
        protocol = models.CharField(ugettext_lazy("Protocol"),max_length=50,choices=PROTOCOL_CHOICES,editable=True,help_text=ugettext_lazy("Board type and protocol for serial comunication"),default='onenet')
        region = models.CharField(ugettext_lazy("Region"),max_length=50,choices=REGION_CHOICES,editable=True)
        channel = models.CharField(ugettext_lazy("Channel"),max_length=50,choices=CHANNEL_CHOICES,editable=True)
	nid = models.CharField(ugettext_lazy("Network ID"),max_length=11,unique=True,editable=True)
	invite = models.CharField(ugettext_lazy("Device ID"),max_length=9,unique=True,editable=True)

        memdump_master_param = models.TextField(ugettext_lazy("memdump master_param"),editable=True,null=True,default=None,blank=True)
        memdump_base_param = models.TextField(ugettext_lazy("memdump base_param"),editable=True,null=True,default=None,blank=True)
        memdump_client_list = models.TextField(ugettext_lazy("memdump client_list"),editable=True,null=True,default=None,blank=True)
        memdump_peer = models.TextField(ugettext_lazy("memdump peer"),editable=True,null=True,default=None,blank=True)

	free = models.BooleanField(ugettext_lazy("Activate all"),default=False)
        active = models.BooleanField(ugettext_lazy("Active"),default=True)

        def __unicode__(self):
            return self.name.__str__()+" NID:"+self.nid.__str__()


class Client(models.Model):

    master = models.ForeignKey(Master)
    #name = models.CharField(ugettext_lazy("Nome"),max_length=50,validators=[validate_name],editable=True)
    name = models.CharField(ugettext_lazy("Nome"),max_length=50,unique=True,editable=True)
    did = models.PositiveSmallIntegerField(ugettext_lazy("Client identification"),editable=True,help_text=ugettext_lazy("Device ID (onenet/oneway)"))
    invite = models.CharField(ugettext_lazy("Device identification"),max_length=50,unique=True,editable=True,help_text=ugettext_lazy("Invite Code (onenet)"))

    memdump_base_param = models.TextField(ugettext_lazy("memdump base_param"),editable=True,null=True,default=None,blank=True)
    memdump_peer = models.TextField(ugettext_lazy("memdump peer"),editable=True,null=True,default=None,blank=True)

    active = models.BooleanField(ugettext_lazy("Attivo"),default=True)

    lasttransaction = models.DateTimeField(ugettext_lazy('Data ultima transazione'),default=timezone.now,editable=True)
    laststatus = models.CharField(ugettext_lazy("stato dell'ultima transazione"),max_length=50,null=True,editable=True,default="SUCCESS")

    pin0state = models.CharField(ugettext_lazy("Pin 0 state"),max_length=7,choices=PINSTATE_CHOICES,null=True,default='output',editable=True)
    pin0onoff = models.PositiveSmallIntegerField(ugettext_lazy("Pin 0 onoff"),null=True,editable=True,default="0",\
                                                     validators=[validate_onoff])

    pin1state = models.CharField(ugettext_lazy("Pin 1 state"),max_length=7,choices=PINSTATE_CHOICES,null=True,default='output',editable=True)
    pin1onoff = models.PositiveSmallIntegerField(ugettext_lazy("Pin 1 onoff"),null=True,editable=True,default="0",\
                                                     validators=[validate_onoff])

    pin2state = models.CharField(ugettext_lazy("Pin 2 state"),max_length=7,choices=PINSTATE_CHOICES,null=True,default='input',editable=True)
    pin2onoff = models.PositiveSmallIntegerField(ugettext_lazy("Pin 2 onoff"),null=True,editable=True,default="1",\
                                                     validators=[validate_onoff])
    pin3state = models.CharField(ugettext_lazy("Pin 3 state"),max_length=7,choices=PINSTATE_CHOICES,null=True,default='input',editable=True)
    pin3onoff = models.PositiveSmallIntegerField(ugettext_lazy("Pin 3 onoff"),null=True,editable=True,default="1",\
                                                     validators=[validate_onoff])

    lastcommand = models.DateTimeField(ugettext_lazy('Data ultimo comando'),auto_now_add=True,editable=False)


    zone = models.ForeignKey(Zone,null=True,blank=True,editable=True)
    floor = models.ForeignKey(Floor,null=True,blank=True,editable=True)
    room = models.ForeignKey(Room,null=True,blank=True,editable=True)
        
    def boardstatus(self):
        if self.laststatus == "SUCCESS":
            return ugettext_lazy("OK")
        else:
            return ugettext_lazy('Broken')
    
    boardstatus.short_description = ugettext_lazy('board status')


    def onoff0(self):
        if self.pin0onoff == 1:
            return ugettext_lazy("On")
        else:
            return ugettext_lazy('Off')
    
    onoff0.short_description = ugettext_lazy('Pin0 status')

    def onoff1(self):
        if self.pin1onoff == 1:
            return ugettext_lazy("On")
        else:
            return ugettext_lazy('Off')
    
    onoff1.short_description = ugettext_lazy('Pin1 status')

    def onoff2(self):
        if self.pin2onoff == 1:
            return ugettext_lazy("On")
        else:
            return ugettext_lazy('Off')
    
    onoff2.short_description = ugettext_lazy('Pin2 status')

    def onoff3(self):
        if self.pin3onoff == 1:
            return ugettext_lazy("On")
        else:
            return ugettext_lazy('Off')
    
    onoff3.short_description = ugettext_lazy('Pin3 status')


    def __unicode__(self):
        return self.name.__str__()+" DID:"+self.did.__str__()


#class Pin(models.Model):
#
#    pin= models.ManyToManyField(client)
#    name = models.CharField(ugettext_lazy("Nome"),max_length=50,editable=True)
#    pinnumber = models.IntegerField(ugettext_lazy("Pin number"),editable=True)
#    pinstate = models.CharField(ugettext_lazy("Pin state"),max_length=6,choices=PINSTATE_CHOICES,editable=True)
#    pinonoff = models.PositiveSmallIntegerField(ugettext_lazy("Pin onoff"),unique=True,editable=True)


class Ticket(models.Model):

    client = models.ForeignKey(Client,null=True,blank=True)
    ticket = models.AutoField(primary_key=True,editable=False)
    aperto = models.BooleanField(ugettext_lazy("Risolto"),default=False,help_text='To set when solved only')
#    date = models.DateTimeField('Data inserimento',auto_now_add=True,editable=False)
    date = models.DateTimeField(ugettext_lazy('Open data'),default=timezone.now)
    priorita = models.IntegerField(ugettext_lazy('Priority'),default=2, choices=PRIORITY_CODES)
    nome = models.CharField(ugettext_lazy('User name'),null=True,max_length=40)
    descrizione= models.CharField(ugettext_lazy('Problem description'),max_length=80)

    def was_recorded_today(self):
        return self.date.date() == datetime.date.today()
    
    was_recorded_today.short_description = ugettext_lazy('Inserted today?')

    def aperto_txt(self):

        if ( self.aperto ):
            return ugettext('Open')
        else:
            return ugettext('Solved')

    def __unicode__(self):
        return self.nome+" "+self.date.__str__()+" "+self.aperto_txt()

class Action(models.Model):

    ticket = models.ForeignKey(Ticket)
#    last_date = models.DateTimeField('Data ultima azione',auto_now=True,blank=True,editable=True)
    last_date = models.DateTimeField(ugettext_lazy('Last action description'),default=timezone.now)
    last_descrizione= models.CharField(ugettext_lazy('Last action description'),max_length=80,blank=True)


    def __unicode__(self):
        return self.last_date.isoformat()
