#!/usr/bin/python
# GPL. (C) 2007-2009 Paolo Patruno.

import os
from configobj import ConfigObj,flatten_errors
from validate import Validator

import platform
if platform.system() == "Linux":
    config_site_file = '/etc/pyonenet/pyonenet-site.cfg'
    config_user_file = '~/.pyonenet.cfg'
    config_file      = 'pyonenet.cfg'
else:
    config_site_file = 'c:\pyonenet-site_win.cfg'
    config_user_file = '~/.pyonenet_win.cfg'
    config_file      = 'pyonenet_win.cfg'


configspec={}

configspec['pyonenetd']={}

configspec['pyonenetd']['logfile']       = "string(default='/tmp/pyonenetd.log')"
configspec['pyonenetd']['lockfile']      = "string(default='/tmp/pyonenetd.lock')"
configspec['pyonenetd']['timestampfile'] = "string(default='/tmp/pyonenetd.timestamp')"
configspec['pyonenetd']['locale']        = "string(default='it_IT.UTF-8')"
configspec['pyonenetd']['user']          = "string(default=None)"
configspec['pyonenetd']['group']         = "string_list(default=None)"
configspec['pyonenetd']['receivetime']   = "integer(default=60)"
configspec['pyonenetd']['recover_minutes']   = "integer(default=60)"
configspec['pyonenetd']['transactionrefresh']= "integer(default=180)"


config    = ConfigObj (config_site_file,file_error=False,configspec=configspec,)

usrconfig = ConfigObj (os.path.expanduser(config_user_file),file_error=False)
config.merge(usrconfig)

usrconfig = ConfigObj (config_file,file_error=False)
config.merge(usrconfig)

val = Validator()
test = config.validate(val,preserve_errors=True)
for entry in flatten_errors(config, test):
    # each entry is a tuple
    section_list, key, error = entry
    if key is not None:
       section_list.append(key)
    else:
        section_list.append('[missing section]')
    section_string = ', '.join(section_list)
    if error == False:
        error = 'Missing value or section.'
    print section_string, ' = ', error
    raise error

# section pyonenetd

logfile       = config['pyonenetd']['logfile']
lockfile      = config['pyonenetd']['lockfile']
timestampfile = config['pyonenetd']['timestampfile']
user          = config['pyonenetd']['user']
group         = config['pyonenetd']['group']
receivetime   = config['pyonenetd']['receivetime']
recover_minutes  = config['pyonenetd']['recover_minutes']
transactionrefresh= config['pyonenetd']['transactionrefresh']

import locale
locale.setlocale(locale.LC_ALL, config['pyonenetd']['locale'])


####

from django.core.management import setup_environ
import settings
setup_environ(settings)

