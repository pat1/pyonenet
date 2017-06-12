%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()"
)}
%{!?python_sitearch: %define python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(
1)")}

%define name pyonenet
%define version 1.2
%define release 1%{?dist}

Summary: automation for home and other
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{version}.tar.gz
License: GPL
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Paolo Patruno <p.patruno@iperbole.bologna.it>
Url: http://pyonenet.sf.net
BuildRequires: python-configobj , Django >= 1.2.3 , help2man
Requires: python-configobj , Django >= 1.2.3,  python-docutils, pyserial

%description

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

%prep
%setup -n %{name}-%{version} -n %{name}-%{version}

%build
%{__python} setup.py build

%install
%{__python} setup.py install --single-version-externally-managed --root=$RPM_BUILD_ROOT

%{__install} -d %{buildroot}%{_var}/{run/pyonenet,log/pyonenet}


%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)

%doc COPYING README
%config(noreplace) %{_sysconfdir}/pyonenet/pyonenet-site.cfg
%dir %{python_sitelib}/pyonenet
%dir %{python_sitelib}/ocm
%{python_sitelib}/pyonenet/*
%{python_sitelib}/ocm/*
%{python_sitelib}/pyonenet-*
%{_mandir}/man1/*

#%{_datadir}/pyonenet/locale/*
%{_bindir}/pyonenetd
%{_bindir}/pyonenetweb
%{_bindir}/pyonenetctrl

%attr(-,pyonenet,pyonenet) %dir %{_datadir}/pyonenet
%attr(-,pyonenet,pyonenet) %{_datadir}/pyonenet/*

%attr(-,pyonenet,pyonenet) %dir %{_var}/log/pyonenet/
%attr(-,pyonenet,pyonenet) %dir %{_var}/run/pyonenet/


%pre

/usr/bin/getent group pyonenet >/dev/null || /usr/sbin/groupadd  pyonenet
/usr/bin/getent passwd pyonenet >/dev/null || \
        /usr/sbin/useradd  -g pyonenet \
                -c "pyonenet user for radio automation software" pyonenet

#/usr/bin/getent group pyonenet >/dev/null || /usr/sbin/groupadd -r pyonenet
#/usr/bin/getent passwd pyonenet >/dev/null || \
#        /usr/sbin/useradd -r -s /sbin/nologin -d %{_datadir}/pyonenet -g pyonenet \
#                -c "pyonenet user for radio automation software" pyonenet
## Fix homedir for upgrades
#/usr/sbin/usermod --home %{_datadir}/pyonenet pyonenet &>/dev/null
##exit 0


#%post
#
## set some useful variables
#PYONENET="pyonenet"
#CHOWN="/bin/chown"
#ADDUSER="/usr/sbin/adduser"
#USERDEL="/usr/sbin/userdel"
#USERADD="/usr/sbin/useradd"
#GROUPDEL="/usr/sbin/groupdel"
#GROUPMOD="/usr/sbin/groupmod"
#ID="/usr/bin/id"
#
#set -e
#
####
## 1. get current pyonenet uid and gid if user exists.
#if $ID $PYONENET > /dev/null 2>&1; then
#   IUID=`$ID --user $PYONENET`
#   IGID=`$ID --group $PYONENET`
#else
#   IUID="NONE"
#   IGID="NONE"
#fi
#
#####
### 2. Ensure that no standard account or group will remain before adding the
###    new user
##if [ "$IUID" = "NONE" ] || [ $IUID -ge 1000 ]; then # we must do sth :)
##  if ! [ "$IUID" = "NONE" ] && [ $IUID -ge 1000 ]; then
##      # pyonenet user exists but isn't a system user... delete it.
##      $USERDEL $PEERCAST
##      $GROUPDEL $PEERCAST
##  fi
##
#####
#
## 3. Add the system account.
##    Issue a debconf warning if it fails. 
#  if $GROUPMOD $PYONENET > /dev/null 2>&1; then 
#    # peercast group already exists, use --ingroup
#    if ! $ADDUSER --system --disabled-password --disabled-login --home /usr/share/pyonenet --no-create-home --ingroup $PYONENET $PYONENET; then
#      echo "The adduser command failed."
#    fi
#  else
#    if ! $ADDUSER --system --disabled-password --disabled-login --home /usr/share/peercast --no-create-home --group $PYONENET; then
#      echo "The adduser command failed."
#    fi
#  fi
#fi
#set +e
#
####
## 4. change ownership of directory
#$CHOWN -R $PYONENET:$PYONENET /usr/share/pyonenet/
#$CHOWN -R $PYONENET:$PYONENET /var/log/pyonenet/
#$CHOWN -R $PYONENET:$PYONENET /etc/pyonenet/
#$CHOWN -R $PYONENET:$PYONENET /var/run/pyonenet/
