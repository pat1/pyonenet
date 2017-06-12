from models import Giorno, Configure, Eventset, Clientgroup, Schedule, PeriodicSchedule
from django.contrib import admin


class ClientgroupInline(admin.StackedInline):
    model = Clientgroup
    extra=1


class ScheduleInline(admin.StackedInline):
#class ScheduleInline(admin.TabularInline):

    model = Schedule
    extra=2


class PeriodicScheduleInline(admin.TabularInline):
    model = PeriodicSchedule
    extra=2


class GiornoAdmin(admin.ModelAdmin):
	search_fields = ['name']


admin.site.register(Giorno, GiornoAdmin)

class ConfigureAdmin(admin.ModelAdmin):

    list_display = ('sezione','active',\
                        'event_starttime'\
                        ,'event_endtime')

admin.site.register(Configure, ConfigureAdmin)


class ClientgroupAdmin(admin.ModelAdmin):

    list_display = ('clientgroup',)
    search_fields = ['clientgroup']


admin.site.register(Clientgroup, ClientgroupAdmin)


class EventsetAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('eventset',)}),
        ('Event information', {'fields': ('active',
                                          'clientgroups',
                                          'pin0onoff',
                                          'pin1onoff',
                                          'pin2onoff',
                                          'pin3onoff',
                                          )}),
        )
    list_display = ('eventset','active',
                                          'pin0onoff',
                                          'pin1onoff',
                                          'pin2onoff',
                                          'pin3onoff',)
    search_fields = ['eventset']
    list_filter = ['active']
    inlines = [
        ScheduleInline,PeriodicScheduleInline,
        ]


admin.site.register(Eventset, EventsetAdmin)


class ScheduleAdmin(admin.ModelAdmin):
        list_display = ('date','event_done'\
				,'was_scheduled_today')
        list_filter = ['date','event_done']
        search_fields = ['eventset','date']
        date_hierarchy = 'date'

admin.site.register(Schedule, ScheduleAdmin)



class PeriodicScheduleAdmin(admin.ModelAdmin):
    list_display = ('start_date','end_date','time'\
				,'event_done')
    list_filter = ['start_date','end_date','time','giorni','event_done']
    search_fields = ['eventset','giorni']
    date_hierarchy = 'start_date'


admin.site.register(PeriodicSchedule, PeriodicScheduleAdmin)
