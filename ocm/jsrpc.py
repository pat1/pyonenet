#!/usr/bin/env python
# -*- coding: utf-8 -*-
# LGPL3. (C) 2017  Paolo Patruno <p.patruno@iperbole.bologna.it>.
#
#                 jsonrpc (telecomando) serial communication module
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


import warnings
import time
import jsonrpc

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
        warnings.warn("jsrpc: I cannot lock device in not Linux platform")
        status = 0

    else:
        import subprocess
        try:
            status = subprocess.call(['lockdev','-l',device])

        except OSError:
            #raise Exception("lockdev: I cannot execute 'lockdev' executable")
            warnings.warn("jsrpc: I cannot execute 'lockdev' executable")
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
        warnings.warn("jsrpc: I cannot lock device in not Linux platform")
        status = 0

    else:
        import subprocess
        try:
            status = subprocess.call(['lockdev','-u',device])

        except OSError:
            #raise Exception("jsrpc: I cannot execute 'lockdev' executable")
            warnings.warn("jsrpc: I cannot execute 'lockdev' executable")
            status=0

        except:
            status = 255

    return status



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

        self.device=device
        if not self.device is None:
            lockdev(self.device)
            self.transport=jsonrpc.TransportSERIAL(port=device,baudrate=115200, logfunc=jsonrpc.log_file("myrpc.log"))
            self._mgr=jsonrpc.ServerProxy(jsonrpc.JsonRpc20(radio=False,notification=False), self.transport)

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


        #nameclass=None
        #id=str(self.__class__).rfind(".")
        #if id>= 0:
        #    nameclass=str(self.__class__)[id+1:]
        #    #print "expected type:",nameclass,"; here I have:",self.ana["onenet"]
        #if nameclass <> self.ana["onenet"]: raise Exception("The device is not of the expected type (client/master)")


    def display(self):

        print ">>>>>>> jsonrpc object <<<<<<<"

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

        if par == "on":
            return True
        elif par == "off":
            return True
        else:
            raise Exception('The "echo" command called with invalid parameter')    


    def cmd_setni(self,nid,invite=None):
        """
        Handles receiving the setni command and all it's parameters.
        The setni command has the form

        status=True if no error occours
        """
        return True

    def cmd_setdid(self,did=None):
        """
        Handles receiving the setdid command and all it's parameters.

        status=True if no error occours
        """
        return self._mgr.setdid(did=did)
            
    def cmd_changedid(self,olddid=None,did=None):
        """
        Handles receiving the changedid command and all it's parameters.

        status=True if no error occours
        """
        return self._mgr.changedid(olddid=olddid,did=did)
            

    
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


    def cmd_save(self,eeprom=True):
        """
        the save command

        return status:
        status=True if no error occours

        """

        return self._mgr.save(eeprom=eeprom)

    def cmd_remotesave(self,did=None,eeprom=True):
        """
        the save command for a remote client

        return status:
        status=True if no error occours

        """

        return self._mgr.remotesave(did=did,eeprom=eeprom)
    

    def cmd_single(self,other,srcunit=0,dstunit=0,onoff=2):
        """

        """

        try:
            did=other.ana["did"]
        except:
            return False

        #print "single:%03X:high:%d%d4000000%d" % (did,srcunit,dstunit,onoff)
        if did is None:
            raise Exception("client DID (device id) is undefined: possible firmware bug") 

        if other.pinsstate[dstunit] <> "output"  :
            raise Exception("client pin is not for output") 

        #self.sendcmd("P:%04X:%02X:%01X" % (did,dstunit,onoff))        

        status = self._mgr.single(did=did,dstunit=dstunit,onoff=onoff)

        if status:
                other.events.register("single", "end","SUCCESS")
                other._pinsstandingunit=dstunit
                other._pinsstandingonoff=onoff
                other.pins[dstunit]=onoff

        return status


    def cmd_list(self,memdump=False):
        """
        the list command
        L - print the TX id.

        example (id = 2):

        -> L
        <- 2
        status=True if no error occours
        """

        #self.ana[nid] = self._mgr.list()

        #self.ana["onenet"]="Master"
        #self.ana["region"]="EU"
        #self.ana["channel"]="1"
        #self.ana["invitecode"]=line

        #self.pins=[None,None,None,None]
        #self.pinsstate=["output","output",None,None]

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
            time.sleep(1)
            #self._mgr._manageresponse(boards,1)
            if ( time.time() - clock ) >= timeout: break


    def close(self):

        if not self.device is None:
            self.transport.close()        
            unlockdev(self.device)
        #self._mgr.close()


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
