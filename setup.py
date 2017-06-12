from distutils.core import setup
import os

from distutils.command.build import build as build_
from setuptools.command.develop import develop as develop_
from distutils.core import Command
#from buildutils.cmd import Command
#from distutils.cmd import Command

from django.core import management
from django.core.management import setup_environ
from pyonenet import settings
from pyonenet import _version_


import platform
platform=platform.system()

if platform == "Windows":
    import py2exe

setup_environ(settings)


class distclean(Command):
    description = "remove man pages and *.mo files"
    user_options = []   
    boolean_options = []

    def initialize_options(self):
        pass
    
    def finalize_options(self):
        pass

    def run(self):
        import shutil
        from os.path import join
        try:
            shutil.rmtree("man")
        except:
            pass
        for root, dirs, files in os.walk('locale'):
            for name in files:
                if name[-3:] == ".mo":
                    os.remove(join(root, name))

        # remove all the .pyc files
        for root, dirs, files in os.walk(os.getcwd(), topdown=False):
            for name in files:
                if name.endswith('.pyc') and os.path.isfile(os.path.join(root, name)):
                    print 'removing: %s' % os.path.join(root, name)
                    if not(self.dry_run): os.remove(os.path.join(root, name))


class build(build_):

    sub_commands = build_.sub_commands[:]

    if platform == "Linux":
        sub_commands.append(('compilemessages', None))
        sub_commands.append(('createmanpages', None))

class compilemessages(Command):
    description = "generate .mo files from .po"
    user_options = []   
    boolean_options = []

    def initialize_options(self):
        pass
    
    def finalize_options(self):
        pass

    def run(self):
        management.call_command("compilemessages")

class createmanpages(Command):
    description = "generate man page with help2man"
    user_options = []   
    boolean_options = []

    def initialize_options(self):
        pass
    
    def finalize_options(self):
        pass

    def run(self):
        try:
            import subprocess
            subprocess.check_call(["mkdir","-p", "man/man1"])
            subprocess.check_call(["help2man","-N","-o","man/man1/pyonenetd.1","./pyonenetd"])
            subprocess.check_call(["gzip","-f", "man/man1/pyonenetd.1"])
            subprocess.check_call(["help2man","-N","-o","man/man1/pyonenetweb.1","./pyonenetweb"])
            subprocess.check_call(["gzip", "-f","man/man1/pyonenetweb.1"])
            subprocess.check_call(["help2man","-N","-o","man/man1/pyonenetctrl.1","./pyonenetctrl"])
            subprocess.check_call(["gzip", "-f","man/man1/pyonenetctrl.1"])
            subprocess.check_call(["help2man","-N","-o","man/man1/pyonenetcron.1","./pyonenetcron"])
            subprocess.check_call(["gzip", "-f","man/man1/pyonenetcron.1"])
        except:
            pass

# Compile the list of files available, because distutils doesn't have
# an easy way to do this.
package_data = []
data_files = []

for dirpath, dirnames, filenames in os.walk('man'):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if filenames:
        data_files.append(['share/'+dirpath, [os.path.join(dirpath, f) for f in filenames]])


for dirpath, dirnames, filenames in os.walk('media'):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if filenames:
        data_files.append(['share/pyonenet/'+dirpath, [os.path.join(dirpath, f) for f in filenames]])


for dirpath, dirnames, filenames in os.walk('doc'):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if filenames:
        data_files.append(['share/pyonenet/'+dirpath, [os.path.join(dirpath, f) for f in filenames]])

for dirpath, dirnames, filenames in os.walk('locale'):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if filenames:
        data_files.append(['share/pyonenet/'+dirpath, [os.path.join(dirpath, f) for f in filenames]])

for dirpath, dirnames, filenames in os.walk('templates'):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if filenames:
        data_files.append(['share/pyonenet/'+dirpath, [os.path.join(dirpath, f) for f in filenames]])

for dirpath, dirnames, filenames in os.walk('images'):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if filenames:
        data_files.append(['share/pyonenet/'+dirpath, [os.path.join(dirpath, f) for f in filenames]])

if platform == "Linux":
    data_files.append(('/etc/pyonenet',['pyonenet-site.cfg']))
else:
    data_files.append(('.',['pyonenet_win.cfg']))


#for dirpath, dirnames, filenames in os.walk('pyonenet/templates'):
#    # Ignore dirnames that start with '.'
#    for i, dirname in enumerate(dirnames):
#        if dirname.startswith('.'): del dirnames[i]
#    if filenames:
#        for file in filenames:
#            package_data.append('templates/'+ os.path.join(dirname, file))
#
#for dirpath, dirnames, filenames in os.walk('pyonenet/locale'):
#    # Ignore dirnames that start with '.'
#    for i, dirname in enumerate(dirnames):
#        if dirname.startswith('.'): del dirnames[i]
#    if filenames:
#        for file in filenames:
#            package_data.append('locale/'+ os.path.join(dirname, file))

#package_data.append('pyonenet_config')
#package_data.append('settings')

if platform == "Linux":

    setup(name='pyonenet',
          version=_version_,
          description='automation for home and other',
          author='Paolo Patruno',
          author_email='p.patruno@iperbole.bologna.it',
          platforms = ["any"],
          url='http://pyonenet.sf.net',
          cmdclass={'build': build,'compilemessages':compilemessages,'createmanpages':createmanpages,"distclean":distclean},
          packages=['pyonenet', 'pyonenet.onenet','pyonenet.oncron', 'ocm'],
          package_data={'pyonenet.onenet': ['fixtures/*.json']},
          scripts=['pyonenetd','pyonenetweb','pyonenetctrl'],
          data_files = data_files,
          license = "GPL",
          requires= [ "django","reportlab"],
          long_description="""\ 
Pyonenet is developed on the one-net eval board and the Command-Line
Specification Version 1.6.2. http://one-net.info/

Pyonenet manage one or more one-net network. You need at last two eval
board: one master and one client.

Pyonenet can:

* initialize the boards (set Network Id, channel and others)
* create network (invite and join clients, remove ....)
* memload and memdump to e from files
* initialize a Data Base
* insert boards into DataBase
* memload and memdump to e from Data Base
* send single commands to clients
* listen for events from clients (pins changes)
* minitor the one-net network from web
* set pin state of clients from web
* change the pin state to groups of clients with a time-based job
  scheduler: it enables users to schedule pins changes periodically at
  certain times or dates. This is done with a web interface
* logging system to monitor the daemons
* users and groups authorization system
* master board configuration is mantained on the DataBase, so pyonenet
  is master fault error prone (you can change it without rebuild the
  network).  A client fault need to connect a new working client to
  the serial port to reload the config param from DB and save it to
  the flash memory on board
* the pins client status is refreshed in configurable time periods to
  prevent a temporary fault on the clients
* multilanguage web interface
"""
          )

else:
     
    setup(console=['pyonenetweb','pyonenetd','pyonenetctrl'],\
              options={"py2exe":{"pakages":['pyonenet','ocm','django','email']}},
          name='pyonenet',
          version=_version_,
          description='automation for home and other',
          author='Paolo Patruno',
          author_email='p.patruno@iperbole.bologna.it',
          platforms = ["any"],
          url='http://pyonenet.sf.net',
          cmdclass={'build': build,'compilemessages':compilemessages,"distclean":distclean},
          packages=['pyonenet', 'pyonenet.onenet','pyonenet.oncron', 'ocm'],
          package_data={'pyonenet.onenet': ['fixtures/*.json']},
          scripts=['pyonenetd','pyonenetweb','pyonenetctrl'],
          data_files = data_files,
          license = "GPL",
          requires= [ "django","reportlab"],
          long_description="""\ 
Pyonenet is developed on the one-net eval board and the Command-Line
Specification Version 1.6.2. http://one-net.info/

Pyonenet manage one or more one-net network. You need at last two eval
board: one master and one client.

Pyonenet can:

* initialize the boards (set Network Id, channel and others)
* create network (invite and join clients, remove ....)
* memload and memdump to e from files
* initialize a Data Base
* insert boards into DataBase
* memload and memdump to e from Data Base
* send single commands to clients
* listen for events from clients (pins changes)
* minitor the one-net network from web
* set pin state of clients from web
* change the pin state to groups of clients with a time-based job
  scheduler: it enables users to schedule pins changes periodically at
  certain times or dates. This is done with a web interface
* logging system to monitor the daemons
* users and groups authorization system
* master board configuration is mantained on the DataBase, so pyonenet
  is master fault error prone (you can change it without rebuild the
  network).  A client fault need to connect a new working client to
  the serial port to reload the config param from DB and save it to
  the flash memory on board
* the pins client status is refreshed in configurable time periods to
  prevent a temporary fault on the clients
* multilanguage web interface
"""
          )

