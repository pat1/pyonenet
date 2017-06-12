from django.db import models
from django.utils.translation import ugettext_lazy
import datetime
import calendar
from pyonenet.pyonenet_config import *
from django.core.exceptions import ValidationError

from pyonenet.onenet.models import Client

def validate_onoff(value):
    if value != 0 and value != 1 and not value is None:
        raise ValidationError(u'%s is not 0 or 1 (or None)' % value)

def giorno_giorno():
	giorni=[]
	for giorno in (calendar.day_name):
		giorno=giorno.decode('utf-8')
		giorni.append(( giorno, giorno))
	return giorni
#	yield 'Tutti','Tutti'

class Giorno(models.Model):

        name = models.CharField(max_length=20,choices=giorno_giorno(),unique=True)
        def __unicode__(self):
            return self.name

class Configure(models.Model):
        sezione = models.CharField(max_length=50,unique=True\
					   ,default='event',editable=False)

	active = models.BooleanField(ugettext_lazy("Activate Events"),default=True)
        event_starttime = models.TimeField(ugettext_lazy('Event start time'))
        event_endtime = models.TimeField(ugettext_lazy('Event start time'))


        def __unicode__(self):
            return self.sezione+" "+self.active.__str__()+" "\
		+self.emission_starttime.isoformat()+" "\
		+self.emission_endtime.isoformat()


class Clientgroup(models.Model):
	clientgroup = models.CharField(ugettext_lazy('Group name'),max_length=200)
        description = models.TextField(ugettext_lazy("Description"),editable=True,null=True,default=None,blank=True)
	clients = models.ManyToManyField(Client)

	def __unicode__(self):
		return self.clientgroup


class Eventset(models.Model):
	eventset = models.CharField(ugettext_lazy('Event name'),max_length=200)
	active = models.BooleanField(ugettext_lazy("Active"),default=True)
	clientgroups = models.ManyToManyField(Clientgroup)

	pin0onoff = models.PositiveSmallIntegerField(ugettext_lazy("Pin 0 onoff"),null=True,editable=True,default=None,\
							     validators=[validate_onoff],blank=True)
	pin1onoff = models.PositiveSmallIntegerField(ugettext_lazy("Pin 1 onoff"),null=True,editable=True,default=None,\
							     validators=[validate_onoff],blank=True)
	pin2onoff = models.PositiveSmallIntegerField(ugettext_lazy("Pin 2 onoff"),null=True,editable=True,default=None,\
							     validators=[validate_onoff],blank=True)
	pin3onoff = models.PositiveSmallIntegerField(ugettext_lazy("Pin 3 onoff"),null=True,editable=True,default=None,\
							     validators=[validate_onoff],blank=True)

	def __unicode__(self):
        #return self.playlist+" "+self.rec_date.isoformat()
		return self.eventset+" "+self.active.__str__()

class Schedule(models.Model):

#    program = models.ForeignKey(Program, edit_inline=models.TABULAR,\
#    num_in_admin=2,verbose_name='si riferisce al programma:',editable=False)

    eventset = models.ForeignKey(Eventset, verbose_name=\
					ugettext_lazy('refer to Eventset:'))

    date = models.DateTimeField(ugettext_lazy('Programmed date'))

# da reinserire !
#    start_date = models.DateField('Data inizio programmazione',null=True,blank=True)
#    end_date = models.DateField('Data fine programmazione',null=True,blank=True)
#    time = models.TimeField('Ora programmazione',null=True,blank=True)
#    giorni = models.ManyToManyField(Giorno,verbose_name='Giorni programmati',null=True,blank=True)
    
    event_done = models.DateTimeField(ugettext_lazy('Event done')\
			        ,null=True,editable=False )

#    def emitted(self):
#	    return self.emission_done != None 
#    emitted.short_description = 'Trasmesso'

    def was_scheduled_today(self):
        return self.date.date() == datetime.date.today()
    
    was_scheduled_today.short_description = ugettext_lazy('Programmed for today?')

    def __unicode__(self):
        return unicode(self.eventset)

class PeriodicSchedule(models.Model):

#    program = models.ForeignKey(Program, edit_inline=models.TABULAR,\
#    num_in_admin=2,verbose_name='si riferisce al programma:',editable=False)

    eventset = models.ForeignKey(Eventset,verbose_name=\
					ugettext_lazy('refer to Eventset:'))

    start_date = models.DateField(ugettext_lazy('Programmed start date'),null=True,blank=True)
    end_date = models.DateField(ugettext_lazy('Programmed end date'),null=True,blank=True)
    time = models.TimeField(ugettext_lazy('Programmed time'),null=True,blank=True)
    giorni = models.ManyToManyField(Giorno,verbose_name=ugettext_lazy('Programmed days'),blank=True)
    
    event_done = models.DateTimeField(ugettext_lazy('Event done')\
			        ,null=True,editable=False )

#    def emitted(self):
#	    return self.emission_done != None 
#    emitted.short_description = 'Trasmesso'

    def file(self):
        return self.playlist.playlist
    file.short_description = ugettext_lazy('Linked Playlist')

    def __unicode__(self):
        return unicode(self.eventset)

