from django.contrib import admin
from models import Master,Client
from models import Ticket,Action,Zone,Floor,Room

admin.site.register(Zone)
admin.site.register(Floor)
admin.site.register(Room)



class MasterAdmin(admin.ModelAdmin):


        fieldsets = (
            (None,{'fields': ('name','device','free','active','protocol')}),
            ('onenet', {'classes': ('collapse',),'fields': (
	     'region','channel','nid','invite','memdump_master_param','memdump_base_param',
	     'memdump_client_list','memdump_peer')}))

        list_display = ('name','free','active','device','protocol','region','channel','nid','invite')
        list_filter = ['active','free','active','protocol','region','channel']
        search_fields = ['name']

        list_display_links = ('name','device','nid','invite')


admin.site.register(Master,MasterAdmin)


class ClientAdmin(admin.ModelAdmin):

        fieldsets = (
            (None,{'fields': ('name','active',"floor","zone","room")}),
            ('onenet', {'classes': ('collapse',),'fields': ('master','did','invite','lasttransaction','laststatus',
		       'memdump_base_param','memdump_peer')}),
            ('pins', {'classes': ('collapse',),'fields': ('pin0state','pin0onoff','pin1state','pin1onoff',\
                                                          'pin2state','pin2onoff','pin3state','pin3onoff',)}),
            )

        list_display = ('master','name','onoff0','onoff1','onoff2','onoff3','boardstatus','did','invite','active','zone','floor','room')
        list_filter = ['master','floor','zone','room','pin0state','pin0onoff','pin1state','pin1onoff',\
                           'pin2state','pin2onoff','pin3state','pin3onoff','zone','floor','room']
        search_fields = ['master','name','did','invite','nome','zone','floor','room']
        date_hierarchy = 'lasttransaction'

        list_display_links = ('master','name','did','invite')


admin.site.register(Client,ClientAdmin)



class ActionInline(admin.TabularInline):
    model = Action
    extra=1
    max_num=3

class TicketAdmin(admin.ModelAdmin):

        fieldsets = [
            ('Ticket', {'fields': [ 'aperto','date','priorita']}),
            ('segnalazione', {'classes': ('wide',),'fields': ['nome','descrizione','client']}),
            ]

        list_display = ('ticket', 'date', 'aperto','priorita','nome','descrizione','client')
        list_filter = ['date','aperto','priorita','client']
        search_fields = ['nome']
        date_hierarchy = 'date'
	inlines = [
        ActionInline,
	]

        list_display_links = ('ticket', 'date')


admin.site.register(Ticket, TicketAdmin)


class ActionAdmin(admin.ModelAdmin):

        list_display = ('ticket', 'last_date','last_descrizione')


admin.site.register(Action, ActionAdmin)

