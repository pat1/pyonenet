# -*- coding: utf-8 -*-
from django.db import models, migrations

def createadmin(apps, schema_editor):

    #print ""
    #print "Insert password for  user 'pyonenet' (administrator superuser)"
    #call_command("createsuperuser",username="pyonenet",email="pyonenet@casa.it") 
    from django.core.management import call_command
    call_command("createsuperuser",username="pyonenet",email="pyonenet@casa.it",interactive=False) 

    from django.contrib.auth.models import User
    u = User.objects.get(username__exact='pyonenet')
    u.set_password('pyonenet')
    u.save()

def deleteadmin(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('onenet', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(createadmin, reverse_code=deleteadmin),
    ]
