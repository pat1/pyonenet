#!/usr/bin/env python
# -*- coding: utf-8 -*-
# LGPL3. (C) 2010  Paolo Patruno <p.patruno@iperbole.bologna.it>.
#
#                 oneway (telecomando) serial communication module
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


import serial,warnings
import time,datetime

log = False

def lockdev(device=None):
    """
    lock a device in Unix UUcp standard mode
    do this only on Linux system

    return 0 on success

    reference:
    http://www.bigwebmaster.com/General/Howtos/Serial-HOWTO-13.html
    http://packages.debian.org/unstable/source/lockdev
    """

    import platform

    if platform.system() <> "Linux":
        warnings.warn("onenet: I cannot lock device in not Linux platform")
        status = 0

    else:
        import subprocess
        try:
            status = subprocess.call(['lockdev','-l',device])

        except OSError:
            #raise Exception("lockdev: I cannot execute 'lockdev' executable")
            warnings.warn("onenet: I cannot execute 'lockdev' executable")
            status=0

        except:
            status = 255

    return status

def unlockdev(device=None):
    """
    unlock a device in Unix UUcp standard mode
    do this only on Linux system

    return 0 on success
    """

    import platform

    if platform.system() <> "Linux":
        warnings.warn("onenet: I cannot lock device in not Linux platform")
        status = 0

    else:
        import subprocess
        try:
            status = subprocess.call(['lockdev','-u',device])

        except OSError:
            #raise Exception("onenet: I cannot execute 'lockdev' executable")
            warnings.warn("onenet: I cannot execute 'lockdev' executable")
            status=0

        except:
            status = 255

    return status


class Mgrser:
    """
    Manage serial communications
    open and close device
    manage async mesaages etc.
    """

    def __init__ (self,device=None):
        """
        lock and open serial device
        """

        self.device = device
        self.line = ""
        self._linecycle = True

        # Log on file.
        if log : self.log_file = open(str(time.time())+".log","w")

        if self.device is None: return

        if lockdev(self.device) <> 0 :
            raise Exception("cannot lock device: "+self.device)

        self._s=serial.Serial(port=self.device,baudrate=9600, bytesize=serial.EIGHTBITS,
                             parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, 
                             timeout=.1, xonxoff=False, rtscts=False, 
                             writeTimeout=10, dsrdtr=False)

#        self._s=serial.Serial(port=self.device,baudrate=9600, bytesize=serial.EIGHTBITS,
#                             parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, 
#                             timeout=.1, xonxoff=False, rtscts=False, 
#                             writeTimeout=10, dsrdtr=False)
#        self._s.open()

    def write(self,command):
        """
        output command to serial port
        """
        if log: self.log_file.write("%"+command+"\n")
        self._s.write(command+"\n")


    def close(self):
        """
        close and unlock serial device
        """

        if self.device is None: return

        self._s.close()

        if unlockdev(self.device) <> 0 :
            raise Exception("cannot lock device: "+self.device)

        if log: self.log_file.write("close\n")
        if log: self.log_file.close()

    def waitline(self,sleepsec=None):
        """ 
        wait for data on serial line and return line 
        when data are present or sleepsec is passed
        """
        
        clock=time.time()

        line=self._s.readline()
        if log: self.log_file.write("#"+line)

#        if         line.rstrip('\a\b\t\f\r\n\0 ') == "ocm-m>"\
#                or line.rstrip('\a\b\t\f\r\n\0 ') == "ocm-c>"\
#                or line.rstrip('\a\b\t\f\r\n\0 ') == "ocm-s>":
#            line=""

        line=line.rstrip('\a\b\t\f\r\n\0 ')

        while line.rstrip('\a\b\t\f\r\n\0 ') == "" :

            line=self._s.readline()
            if log: self.log_file.write("#"+line)

#            if     line.rstrip('\a\b\t\f\r\n\0 ') == "ocm-m>"\
#                or line.rstrip('\a\b\t\f\r\n\0 ') == "ocm-c>"\
#                or line.rstrip('\a\b\t\f\r\n\0 ') == "ocm-s>":
#                line = ""
            line=line.rstrip('\a\b\t\f\r\n\0 ')

            if sleepsec is None: break
            delta=time.time() - clock
            if delta >= sleepsec: break
            #print "manca ancora",(sleepsec-delta)

        #print "torno:",line
        return line


    def pushline(self,sleepsec=10):
        """
        get a new line only when the new line was digested
        raise on line not digested
        """

        if not self._linecycle and self.line <> "":
            tmpline=self.line
            self.line = ""
            raise Exception("line not managed: >"+tmpline+"<")

        if self.line == "":
            self._linecycle = False
            self.line = self.waitline(sleepsec)

        return self.line

    def popline(self):
        """
        say that a line was digested
        """
        self.line = ""
        self._linecycle = True
        return self.line


    def _manageresponse(self, boards=(), sleepsec=3):
        """
        read a line from serial and manage response for async transaction
        """

        return self.pushline(sleepsec)


    def _checkok(self,line):
        """
        return relative,status:
        relative=True if message is "OK"
        status=True if no error occours
        """                  
        #print "aspetto ok trovo",line
        if line.find("OK") >= 0:
            self.popline()
            return True
        else:
            return False


class Asyncevent:

    def __init__ (self,timeout=10):

        self.events = {}
        self.timeout=timeout

    def register(self, command, event=None, status=None):
        """
        register async event
        """
        #print "registro:",command, event, status
        self.events[command]={}
        self.events[command]["status"] = status
        self.events[command]["event"]  = event
        self.events[command]["stime"]  = time.time()

    def unregister(self,command):
        """
        remove async event
        """
        try:
            self.events[command] = {}

        except:
            pass

    def check(self,command,timeout=None):
        """
        check async event
        when timeout time is passed starting fron "start" event, the event is set to "timeout"
        and status to "failed"
        """
        if timeout is None: timeout = self.timeout

        try:
            status = self.events[command]["status"]
            stime  = self.events[command]["stime"]
            event  = self.events[command]["event"]
        except:
            return "stop"

        etime=time.time()

        if ( etime - stime ) > timeout and event == "start" :
            event = "timeout"
            status = "failed"
            self.events[command]["event"] = event
            self.events[command]["status"] = status

        return event

    def getstatus(self,command,timeout=None):
        """
        check async event
        """
        self.check(command,timeout)

        try:
            status = self.events[command]["status"]
        except:
            return None

        return status



class Eval:

    def __init__ (self, device=None, did=None,invitecode=None,\
                      pins=[None,None,None,None],pinsstate=["output",None,None,None],memdump=False):

        self._mgr=Mgrser(device)

        self.ana = dict.fromkeys(("onenet","nid","did","invitecode","region","channel","version","invitecode","status","nsmkey","smkey"), None)
        self.clients=[]
        self.events = Asyncevent()

        self.ana["did"] = did
        self.ana["invitecode"] = invitecode
        self.pins=pins
        self.pinsstate=pinsstate

        self._pinsstandingunit = None
        self._pinsstandingonoff = None

        self._mem = dict.fromkeys(("master_param","base_param","client_list","peer"), None)

        if device is None: return

        self._mgr.popline()
        self._mgr.pushline(sleepsec=.3)

        time.sleep(.3)

        self.sendcmd("")

        self._mgr.popline()
        self._mgr.pushline(sleepsec=.3)
        self._mgr.popline()

        time.sleep(.3)

        status=self.cmd_echo("off")
        if not status: raise Exception("Device do not respond (connect and switch on): cannot set echo off on device")

        status=self.cmd_list(memdump=False)
        if not status: raise Exception("Cannot cmd_list on device")

        nameclass=None
        id=str(self.__class__).rfind(".")
        if id>= 0:
            nameclass=str(self.__class__)[id+1:]
            #print "expected type:",nameclass,"; here I have:",self.ana["onenet"]
        if nameclass <> self.ana["onenet"]: raise Exception("The device is not of the expected type (client/master)")



    def sendcmd(self,command):

        self._mgr.write(command)

    def display(self):

        print ">>>>>>> ONE-NET object <<<<<<<"

        for ana in self.ana:
            print ana,":",self.ana[ana]
        print "Pins state :", self.pinsstate
        print "Pins :", self.pins
        print "Memory : ", self._mem

        print ">>>>>>>----------------<<<<<<<"
        return True

    def cmd_echo(self,par):
        """
        the echo command

        return status:
        status=True if no error occours
        """

        #clean communication
        #self._mgr.waitline(sleepsec=1)

        if par == "on":
            self.sendcmd("E:"+"1")
        elif par == "off":
            self.sendcmd("E:"+"0")
        else:
            raise Exception('The "echo" command called with invalid parameter')
            
        line=self._mgr._manageresponse()
        while line.find("E:") >= 0 :
            self._mgr.popline()
            line=self._mgr._manageresponse()

        return self._mgr._checkok(line)


    def cmd_setni(self,nid,invite=None):
        """
        Handles receiving the setni command and all it's parameters.
        The setni command has the form

        C - change the id of the master.

        C:N

        where:

        * N is the new address [0:f]
        
        reply to the 'C' command can be:
        
        * "OK" the address has changed.
        * "ko" some error occured.
        
        example:

        -> C:D
        <- OK
        
        will change the master address 0x0 to 0xD.

        status=True if no error occours
        """

        if invite is not None :
            raise Exception('The "setni" command do not use invite that is set to :'+str(invite))
            

        self.sendcmd("C:"+str(nid))

        line=self._mgr._manageresponse()
        return self._setni_response(line)


    def _setni_response(self,line):
        """
        return False if no new line to read
        """

        return self._mgr._checkok(line)


    def cmd_user_pin(self,pinnumber,pinstate):
        """
        The user pin command is used to configure individual input/output pins.
        A user pin set to “input” will, when toggled, send a simple switch
        message to its assigned peers; one set to “output” will assert that
        pin based on a received Switch message destined for its associated Unit.

        return status:
        status=True if no error occours

        NOOP command
        """

        return True


    def cmd_save(self):
        """
        the save command

        return status:
        status=True if no error occours

        NOOP command
        """

        return True


    def cmd_single(self,other,srcunit=0,dstunit=0,onoff=2):
        """
        P - send a command to a remote.

        P:AAAA:PP:C

        where

        * AAAA is the address ascii - hex from 0001 to FFFF where:
          o 0000 unconfigured device.
          o FFFF is broadcast address.
        * PP is the pin number in Ascii/hex form from 00 to FF where:
          o 00 - i/o pin 0
          o 01 - i/o pin 1
          o FF - All pin
        * C is the command in ascii/hex where:
          o 0 is off.
          o 1 is on.

        reply to the 'P' command can be:

        * "OK" the command is received and forwarded to the clients.
        * "ko" some error occured.

        example

        -> P:012F:01:1
        <- OK

        will send to the device "012F" the command "turn on the pin 1".

        Note:
        address "0000" is used by unconfigurd devices and should not be used in normal condition.
"""

        try:
            did=other.ana["did"]
        except:
            return False


        self.wait(other,(other,),"single")

        #print "single:%03X:high:%d%d4000000%d" % (did,srcunit,dstunit,onoff)
        if did is None:
            raise Exception("client DID (device id) is undefined: possible firmware bug") 

        if other.pinsstate[dstunit] <> "output"  :
            raise Exception("client pin is not for output") 

        self.sendcmd("P:%04X:%02X:%01X" % (did,dstunit,onoff))
        
        line=self._mgr._manageresponse(boards=(other,))
        status = self._single_response(line)

        if status:
                other.events.register("single", "end","SUCCESS")
                other._pinsstandingunit=dstunit
                other._pinsstandingonoff=onoff
                other.pins[dstunit]=onoff

        return status

    def _single_response(self,line):
        """
        return True if no error occours

        OK              Command initiated successfully
        """

        return self._mgr._checkok(line)


    def cmd_list(self,memdump=False):
        """
        the list command
        L - print the TX id.

        example (id = 2):

        -> L
        <- 2
        status=True if no error occours
        """

        self.sendcmd("L")

        line=self._mgr._manageresponse()

        try:
            self.ana["nid"]=line
            self._mgr.popline()
        except:
            return False

        self.ana["onenet"]="Master"
        self.ana["region"]="EU"
        self.ana["channel"]="1"
        self.ana["invitecode"]=line

        self.pins=[None,None,None,None]
        self.pinsstate=["output","output",None,None]

        return True


    def cmd_channel(self,region="EUR",chan=1):
        """
        NOOP command
        """

        return True

    def wait(self,board,boards, command, timeout=None):
        """
        wait for async command to terminate
        """

        clock=time.time()

        while  board.events.check(command, timeout) == "start" :
            #print "check",board.events.check(command, timeout)
            line=self._mgr._manageresponse(boards,.1)
            if timeout is not None :
                if (time.time() - clock) >= timeout: break
            time.sleep(.1)
            
        #print "check",board.events.check(command, timeout)
        return board.events.check(command, timeout) <> "start"



    def receive(self,boards=(), timeout=5):

        clock=time.time()

        while True:
            self._mgr._manageresponse(boards,1)
            if ( time.time() - clock ) >= timeout: break


    def close(self):

        self._mgr.close()


    def cmd_memdump(self,subset=None):
        """
        Manage memdump command.

        NOOP command
        """

        return False


    def cmd_memload(self,subset=None):
        """
        Manage memload command.

        NOOP command
        """

        return False
