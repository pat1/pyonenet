#!/usr/bin/env python
# -*- coding: utf-8 -*-
# LGPL3. (C) 2010  Paolo Patruno <p.patruno@iperbole.bologna.it>.
#
#                 one-net serial communication module
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
import random
import crc

log = False

def rndkey():
    """
    generate random key
    """

    key=""
    for cc in range(4):
        for c in range(2):
            key+=random.choice('0123456789ABCDEF')
        if cc < 3 : key+="-"

    return key

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
            raise Exception("onenet: I cannot execute 'lockdev' executable")

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

        self._s=serial.serial_for_url(self.device,baudrate=38400, bytesize=serial.EIGHTBITS,
                             parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, 
                             timeout=.1, xonxoff=False, rtscts=False, 
                             writeTimeout=10, dsrdtr=False)

#        self._s=serial.Serial(port=self.device,baudrate=38400, bytesize=serial.EIGHTBITS,
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

    def send(self,command):
        """
        output string to serial port
        """
        if log: self.log_file.write("%"+command+"\n")
        self._s.write(command)

    def abort(self):
        """
        output \n to serial port to interrupt memload sequence
        """
        if log: self.log_file.write("%\n")
        self._s.write("\n")

    def ack(self):
        """
        output ack to serial port
        """
        if log: self.log_file.write("%0\n")
        self._s.write("0\n")

    def nack_resend(self):
        """
        output not ack resend to serial port
        """
        print "warning: resend"
        if log: self.log_file.write("%1\n")
        self._s.write("1\n")

    def nack_abort(self):
        """
        output not ack abort to serial port
        """
        if log: self.log_file.write("%2\n")
        self._s.write("2\n")


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

        if         line.rstrip('\a\b\t\f\r\n\0 ') == "ocm-m>"\
                or line.rstrip('\a\b\t\f\r\n\0 ') == "ocm-c>"\
                or line.rstrip('\a\b\t\f\r\n\0 ') == "ocm-s>":
            line=""
            #print "skippo"

        while line.rstrip('\a\b\t\f\r\n\0 ') == "" :

            line=self._s.readline()
            if log: self.log_file.write("#"+line)

            if     line.rstrip('\a\b\t\f\r\n\0 ') == "ocm-m>"\
                or line.rstrip('\a\b\t\f\r\n\0 ') == "ocm-c>"\
                or line.rstrip('\a\b\t\f\r\n\0 ') == "ocm-s>":
                line = ""
                #print "skippo"

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

        line = self.pushline(sleepsec)


        # ON MASTER

        #  async message for Received Single transaction data from clients
#ocm-m> Received Single transaction data from 002, len 5
#3F 40 00 00 00
#3F 40 00 00 01
#2F 40 00 00 00
#2F 40 00 00 01

        id = line.find('Received Single transaction data from ')
        if id >= 0 :
            did = int(float.fromhex(line[id+38:id+41]))
            self.popline()
            line = self._manageresponse(boards,sleepsec)
            for board in boards:
                if board.ana["did"] == did:
                    board.pins[int(float.fromhex(line[0]))]=line[13]

            self.popline()
            line = self._manageresponse(boards,sleepsec)

        #  async message for change key
        if line.find('Updating NETWORK KEY succeeded') >= 0 :
            for board in boards:
                if board.ana["onenet"] == "Master":
                    board.events.register("change_key","end","SUCCESS")
            self.popline()
            line = self._manageresponse(boards,sleepsec)

            #print "manage async command"

        #  async message for invite
        #">Device 2325-2384 added as 006"
        if line.find('Device ')  >= 0 :   # XXXX-XXXX 
            if line.find('not added') >= 0 :
                status="FAILED"

            if line.find(' added as ') >= 0 :   # YYY
                status="SUCCESS"
                id = line.find(' added as ')
                did = int(float.fromhex(line[id+10:id+13]))
                
            for board in boards:
                if board.ana["onenet"] == "Master":
                    board.events.register("invite","end",status)

                # to do only if client is not cable connected
                if board.ana["onenet"] == "Client":
                    board.ana["did"] = did

            self.popline()


        #  async message for remove device
        #     bad documentation
        #"Device removal of XXX succeeded"
        #if line.find('Device removal of ') >= 0 :

        # remove all "Updating REMOVE DEVICE"
        while line.find('Updating UNASSIGN PEER') >= 0 :
            self.popline()
            self._manageresponse()

        #"ocm-m> Updating REMOVE DEVICE on 003 succeeded."
        id = line.find('Updating REMOVE DEVICE on ')
        if id >= 0 :
            status="FAILED"
            did = int(float.fromhex(line[id+26:id+29]))

            if line.find('succeeded.') >= 0 :
                status="SUCCESS"
                self.popline()
                
            else:
                self.popline()
                self._manageresponse()
                if line.find("Removing device from MASTER table anyhow") >= 0:
                    self.popline()
                
            for board in boards:
                if board.ana["onenet"] == "Master":
                    board.events.register("remove device","end",status)

                # to do only if client is not cable connected
                if board.ana["onenet"] == "Client":
                    board.ana["did"] = None


        # ON MASTER and CLIENT
        #  async message for single
        id = line.find('Single transaction with ')
        if id >= 0 :
            did = int(float.fromhex(line[id+24:id+27]))
            id = line.find('; return status:')
            if id >= 0 :
                status = line[id+17:].rstrip()

            # "SUCCESS"
            # "SINGLE TRANSACTION COMPLETE"
            # "SINGLE TRANSACTION FAILED"

            for board in boards:
                if board.ana["did"] == did:
                    board.events.register("single","end",status)
                    if status == "SUCCESS" :
                        if board._pinsstandingonoff == 2:
                            if not board.pins[board._pinsstandingunit] is None:
                                board.pins[board._pinsstandingunit]=\
                                    (board.pins[board._pinsstandingunit]+1) % 2
                        else:
                            board.pins[board._pinsstandingunit]=board._pinsstandingonoff

            self.popline()
            #line = self._manageresponse(boards,sleepsec)


        # ON CLIENT
        # join command:
        # "Successfully joined network as XXX"
        id = line.find('Successfully joined network as ')
        if id >= 0 :
            did = int(float.fromhex(line[id+32:id+35]))
            for board in boards:
                #print "onenet=",board.ana["onenet"]
                if board.ana["onenet"] == "Client":
                    board.events.register("join","end","SUCCESS")
                    board.ana["did"] = did
            self.popline()
            #line = self._manageresponse(boards,sleepsec)
            #print "manage async command"


        # "Join command timed out.  Device not added."
        id = line.find('Join command timed out.')
        if id >= 0 :
            for board in boards:
                #print "onenet=",board.ana["onenet"]
                if board.ana["onenet"] == "Client":
                    board.events.register("join","end","FAILED")
                    board.ana["did"] = None
            self.popline()
            #line = self._manageresponse(boards,sleepsec)
            #print "manage async command"
        # 
#        if line.find("Single transaction with ") >=0 :
#            id = line.find("return status: ")
#            if id >=0 :
#                if      line[id+15:].find("SUCCESS") < 0 and\
#                        line[id+15:].find("SINGLE TRANSACTION COMPLETE") < 0:
#
#                    raise Exception("Client cannot communicate single to master")
#
#
#                # here the ocm miss pins change messages
#                # I can get it from master only
#
#            self.popline()
#            #line = self._manageresponse(boards,sleepsec)
            
            
        return self.line


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
                      pins=[None,None,None,None],pinsstate=[None,None,None,None],memdump=False):

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

        self._mgr.nack_abort()
        self._mgr.popline()
        self._mgr.pushline(sleepsec=.3)
        self._mgr.popline()
        self._mgr.pushline(sleepsec=.3)

        self._mgr.abort()
        self._mgr.popline()
        self._mgr.pushline(sleepsec=.3)

        self._mgr.popline()
        self._mgr.pushline(sleepsec=.3)

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
        self._mgr.waitline(sleepsec=1)

        self.sendcmd("echo:"+par)
        line=self._mgr._manageresponse()
        while line.find("echo:"+par) >= 0 :
            self._mgr.popline()
            line=self._mgr._manageresponse()

        return self._echo_response(line)


    def _echo_response(self,line):
        """
        return False if no new line to read
        """

        if line.find('The "echo" command failed') >= 0:
            line=self._mgr.popline()
            raise Exception('The "echo" command failed')

        return self._mgr._checkok(line)


    def cmd_setni(self,nid,invite):
        """
        Handles receiving the setni command and all it's parameters.
        The setni command has the form

        setni:123456789:GGGG-HHHH

        where 123456789 is a valid NID 
        (one of the NID's allocated to ONE-NET evaluation boards).
        where GGGG-HHHH is an invite code. 
        It will be repeated to produce the full invite code 
        (GGGG-HHHH-GGGG-HHHH).

        The manufacturing data segment in data flash will contain a
        full SID (where the master DID is appended to the NID).

        return status:
        status=True if no error occours
        """

        self.sendcmd("setni:"+nid+":"+invite)

        line=self._mgr._manageresponse()
        return self._setni_response(line)


    def _setni_response(self,line):
        """
        return False if no new line to read
        """

        if line.find('The "setni" command failed') >= 0:
            line=self._mgr.popline()
            raise Exception('The "setni" command failed')

        return self._mgr._checkok(line)




    def cmd_user_pin(self,pinnumber,pinstate):
        """
        The user pin command is used to configure individual input/output pins.
        A user pin set to “input” will, when toggled, send a simple switch
        message to its assigned peers; one set to “output” will assert that
        pin based on a received Switch message destined for its associated Unit.

        return status:
        status=True if no error occours
        """

        self.sendcmd("user pin:"+pinnumber+":"+pinstate)

        line=self._mgr._manageresponse()
        return self._user_pin_response(line)


    def _user_pin_response(self,line):
        """
        return False if no new line to read
        """

        if line.find('The "user pin" command failed') >= 0:
            line=self._mgr.popline()
            raise Exception('The "user pin" command failed')

        self.pinsstate[pinnumber] = pinstate

        return self._mgr._checkok(line)


    def cmd_save(self):
        """
        the save command

        return status:
        status=True if no error occours
        """

        self.sendcmd("save")
        line=self._mgr._manageresponse()
        return self._mgr._checkok(line)

    def cmd_erase(self):
        """
        the erase command

        return status:
        status=True if no error occours
        """

        self.sendcmd("erase")
        line=self._mgr._manageresponse()
        return self._mgr._checkok(line)


    def cmd_single(self,other,srcunit=0,dstunit=0,onoff=2):

        try:
            did=other.ana["did"]
        except:
            return False


        self.wait(other,(other,),"single")

        #print "single:%03X:high:%d%d4000000%d" % (did,srcunit,dstunit,onoff)
        if did is None:
            raise Exception("client DID (device id) is undefined: possible evaluation application bug") 
        self.sendcmd("single:%03X:low:%01X%01X400000%02X" % (did,srcunit,dstunit,onoff))
        
        line=self._mgr._manageresponse(boards=(other,))
        status = self._single_response(line)

        if status:
                other.events.register("single", "start")
                other._pinsstandingunit=dstunit
                other._pinsstandingonoff=onoff

        return status

    def _single_response(self,line):
        """
        return True if no error occours

        OK                                           Command initiated successfully

        The "single" command failed - invalid format Command not formatted correctly

        The "single" command failed - invalid        Single data can only be sent in Master or
        command for SNIFFER                          Client mode.

        The "single" command failed - required       Resources needed to complete the command
        resources unavailable                        are unavailable

        The "single" command failed - invalid DID    Destination Device/Unit pair does not exist in
        and/or unit                                  the network

        The "single" command failed - device needs   Client is not part of a network and needs to
        to join a network first                      complete the join process before sending

        """

        if line.find('The "single" command failed') >= 0 :
            self._mgr.popline()
            raise Exception('The "single" command failed')


        return self._mgr._checkok(line)


    def cmd_list(self,memdump=False):
        """
        the list command

        return relative,status:
        relative=True if message is list relative
        status=True if no error occours
        """

        self.sendcmd("list")

        line=self._mgr._manageresponse()
        while self._list_response(line):
            line=self._mgr._manageresponse()

        if (line.find("Peer table:") >= 0 ):
            self._mgr.popline()
            line=self._mgr._manageresponse()

            # skip until "User pins"
            while (line.find("User pins:") < 0 ):
                self._mgr.popline()
                line=self._mgr._manageresponse()

        if (line.find("User pins:") >= 0 ):
            self._mgr.popline()
            line=self._mgr._manageresponse()

            found = True
            while found:
                found = False
                id = line.find("input state:" )
                if ( id >= 0):
                    self.pinsstate[int(float.fromhex(line[0:3]))]="input"
                    self.pins[int(float.fromhex(line[0:3]))]=int(line[id+12:])
                    found = True
                    self._mgr.popline()
                    line=self._mgr._manageresponse()

                id = line.find("output state:") 
                if ( id >= 0):
                    self.pinsstate[int(float.fromhex(line[0:3]))]="output"
                    self.pins[int(float.fromhex(line[0:3]))]=int(line[id+13:])
                    found = True
                    self._mgr.popline()
                    line=self._mgr._manageresponse()

                if (line.find("disable") >= 0 ):
                    self.pinsstate[int(float.fromhex(line[0:3]))]="disable"
                    self.pins[int(float.fromhex(line[0:3]))]=None
                    found = True
                    self._mgr.popline()
                    line=self._mgr._manageresponse()

        status=self._mgr._checkok(line)
        if not status:
            return status 

        if (memdump) :
            status = self.cmd_memdump(self.ana["onenet"])

        return status 


    def _list_response(self,line):

        if line.find("ocm-c>") == 0 :
            self.ana["onenet"]="Client"

        if line.find("ocm-m>") == 0 :
            self.ana["onenet"]="Master"


        id=line.find("Client count:")
        if (id >= 0 ):
            id+=13
            self.ana["nclients"]=line[id:-1]
            self.ana["clients"]=[]
            self._mgr.popline()
            return True

        id=line.find("  client")
        if (id >= 0 ):
            idn=id+8
            id=line.find("DID:")
            if (id >= 0 ):
                pos = int(line[idn:id-1])
                id+=4
                did = int(float.fromhex(line[id:-1]))
                self.ana["clients"].insert(pos,did)
                self._mgr.popline()
                return True

        id=line.find("NID: ")
        if (id >= 0 ):
            id+=7
            self.ana["nid"]=line[id:-1]
            self._mgr.popline()
            return True

        id=line.find("DID: ")
        if (id >= 0 ):
            id+=5
            self.ana["did"]=int(float.fromhex(line[id:-1]))
            self._mgr.popline()
            return True

        id=line.find("Version ")
        if (id >= 0 ):
            id+=8
            self.ana["version"]=line[id:id+6]
            self._mgr.popline()
            return True

        id=line.find("Invite code: ")
        if (id >= 0 ):
            id+=13
            self.ana["invitecode"]=line[id:-1]
            self._mgr.popline()
            return True

        id=line.find("Client join status: ")
        if (id >= 0 ):
            id+=20
            self.ana["status"]=line[id:-1]
            self._mgr.popline()
            return True

        id=line.find("Invite code: ")
        if (id >= 0 ):
            id+=13
            self.ana["invitecode"]=line[id:-1]
            self._mgr.popline()
            return True

        id=line.find("Channel: ")
        if (id >= 0 ):
            if line.find("channel not selected")>= 0:
                self.ana["region"]=None
                self.ana["channel"]=None
                #raise Exception("board is not ready: retry after")
            else:
                ch = line[id+9:].split()
                self.ana["region"]=ch[0]
                self.ana["channel"]=ch[1]

            self._mgr.popline()
            return True

        if line.find("Client count:") >= 0 :
            self.clients=[]
            self._mgr.popline()
            return True

        id=line.find("  client")
        if (id >= 0 ):
            id=line[id:].find("DID:")
            if (id >= 0 ):
                id+=4
                did=int(float.fromhex(line[id:-1]))
                self.clients.append(did)
            self._mgr.popline()
            return True

        id = line.find("Non-stream message key")
        if id <0 : id = line.find("Non-strea message key")
        if id >= 0 :
            id = line.find(":")
            self.ana["nsmkey"]=line[id+2:-1]
            self._mgr.popline()
            return True

        id = line.find("Stream message key")
        if id >= 0 :
            id = line.find(":")
            self.ana["smkey"]=line[id+2:-1]
            self._mgr.popline()
            return True

        return False


    def cmd_channel(self,region="EUR",chan=1):

        self.sendcmd("channel:%s:%d"%(region,chan))
        line=self._mgr._manageresponse()
        return self._channel_response(line)


    def _channel_response(self,line):
        """
        return relative,status:
        relative=True if message is channel relative
        status=True if no error occours
        """

        if line.find('The "channel" command failed') >= 0 :
            line=self._mgr.popline()
            raise Exception('The "channel" command failed')

        return self._mgr._checkok(line)


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
        Manage memdump command. the response should be:

        TRANS_START:02D00024:9A
        CHUNK_START:00000014:E0030C0D0E0F76A0249B05D816C594F66EC4DE31:F0
        CHUNK_START:00010014:F709E531BF23010AE131553801013C00B4B31F0A:06
        .....
        CHUNK_START:00230014:0E00003000010100B4D30B112B00003000010100:AA
        OK
        """

        if subset is None:
            subset = self.ana["onenet"]

        if subset == "all":
            status = self.cmd_memdump("master_param")
            if not status:
                return status 
            status = self.cmd_memdump("base_param")
            if not status:
                return status 
            status = self.cmd_memdump("peer")
            if not status:
                return status 
            status = self.cmd_memdump("client_list")
            return status 


        if subset == "Master":
            status = self.cmd_memdump("master_param")
            if not status:
                return status 
            status = self.cmd_memdump("base_param")
            if not status:
                return status 
            #status = self.cmd_memdump("peer")
            #if not status:
            #    return status 
            status = self.cmd_memdump("client_list")
            return status 

        if subset == "Client":
            status = self.cmd_memdump("base_param")
            if not status:
                return status 
            #status = self.cmd_memdump("peer")
            return status 


        print "memdump:",subset
        self.sendcmd("memdump:"+subset)

        line=self._mgr.pushline()


        if line.find('The "memdump" command failed') >= 0:
            self._mgr.popline()
            raise Exception(line)

        if line.find('Invalid command "memdump"') >= 0:
            self._mgr.popline()
            raise Exception(line)


        rep = 0
        mycrc = None

        while (rep < 4):
            rep += 1
            errorstring = 'problems in memdump response (TRANS_START crc)'

            if line.find('TRANS_START') < 0:
                self._mgr.nack_resend()
                self._mgr.popline()
                line=self._mgr.pushline()
                errorstring = 'TRANS_START is missing in memdump response'
                exit
            i=line.find(':')
            if i < 0:
                self._mgr.nack_resend()
                self._mgr.popline()
                line=self._mgr.pushline()
                errorstring = 'problems in memdump response (i)'
                exit

            j=1+i+line[i+1:].find(':')
            if j < 0:
                self._mgr.nack_resend()
                self._mgr.popline()
                line=self._mgr.pushline()
                errorstring = 'problems in memdump response (j)'
                exit

            mycrc=hex(int(line[j+1:-1],16))
            oncrc= hex(crc.one_net_compute_crc(line[i+1:i+9]))

            if (mycrc != oncrc ) :
                self._mgr.nack_resend()
            else:
                self._mgr.ack()
                size=int(float.fromhex("0X"+line[i+1:i+5]))
                nchunk=int(float.fromhex("0X"+line[i+5:i+9]))
                self._mgr.popline()
                line=self._mgr.pushline()
                break

            self._mgr.popline()
            line=self._mgr.pushline()

        if ( rep >= 4 ):
            self._mgr.nack_abort()
            raise Exception(errorstring)

        rep = 0
        nch = 0
        mycrc = None
        mem = ""

        while (rep < 4 and nch < nchunk):
            rep += 1
            errorstring = 'problems in memdump response (CHUNK crc)'
            if line.find('CHUNK_START') < 0:
                self._mgr.nack_resend()
                line=self._mgr.popline()
                line=self._mgr.pushline()
                errorstring = 'CHUNK_START is missing in memdump response'
                exit

            i=line.find(':')
            if i < 0:
                self._mgr.nack_resend()
                self._mgr.popline()
                line=self._mgr.pushline()
                errorstring = 'problems in memdump response (i)'
                exit

            j=1+i+line[i+1:].find(':')
            if j < 0:
                self._mgr.nack_resend()
                self._mgr.popline()
                line=self._mgr.pushline()
                errorstring= 'problems in memdump response (j)'
                exit

            k=1+j+line[j+1:].find(':')
            if k < 0:
                self._mgr.nack_resend()
                self._mgr.popline()
                line=self._mgr.pushline()
                errorstring = 'problems in memdump response (k)'
                exit

            mycrc=hex(int(line[k+1:-1],16))

            nchu=int(float.fromhex("0X"+line[i+1:i+5]))
            ndigit=int(float.fromhex("0X"+line[i+5:i+9]))
            realndigit = len(line[j+1:k])/2

            oncrc= hex(crc.one_net_compute_crc(line[j+1:k]))

            if (mycrc != oncrc or realndigit != ndigit or nchu != nch  ) :
                self._mgr.nack_resend()

            else:
                self._mgr.ack()
                rep = 0
                nch += 1
                mem += line[j+1:k]

            self._mgr.popline()
            line=self._mgr.pushline()

        if ( rep >= 4 ):
            self._mgr.nack_abort()
            raise Exception(errorstring)

        status =self._mgr._checkok(line)

        if status :
            self._mem[subset] = mem

        return status



    def cmd_memload(self,subset=None):
        """
        Manage memload command. the protocol should be:

        TRANS_START:02D00024:9A
        CHUNK_START:00000014:E0030C0D0E0F76A0249B05D816C594F66EC4DE31:F0
        CHUNK_START:00010014:F709E531BF23010AE131553801013C00B4B31F0A:06
        .....
        CHUNK_START:00230014:0E00003000010100B4D30B112B00003000010100:AA
        OK
        """

        if subset is None:
            subset = self.ana["onenet"]
            
        if subset == "all":
            status = self.cmd_memload("master_param")
            if not status:
                return status 
            status = self.cmd_memload("base_param")
            if not status:
                return status
            status = self.cmd_memload("peer")
            if not status:
                return status 
            status = self.cmd_memload("client_list")
            return status

        if subset == "Master":
            status = self.cmd_memload("master_param")
            if not status:
                return status 
            status = self.cmd_memload("base_param")
            if not status:
                return status
            #status = self.cmd_memload("peer")
            #if not status:
            #    return status 
            status = self.cmd_memload("client_list")
            return status

        if subset == "Client":
            status = self.cmd_memload("base_param")
            if not status:
                return status
            #status = self.cmd_memload("peer")
            return status 

        print "memload:", subset
        self.sendcmd("memload:"+subset)
        self._mgr.popline()
        line=self._mgr.pushline(0)

        if line.find('The "memload" command failed') >= 0:
            self._mgr.popline()
            raise Exception(line)

        if line.find('Invalid command "memload"') >= 0:
            self._mgr.popline()
            raise Exception(line)


        rep = 0
        mycrc = None
        retry = True

        if not (self._mem[subset] is None):
            size=len(self._mem[subset])/2
        else:
            return False

        nchunk=size/20 
        if ( size % 20) > 0:
            nchunk += 1
        sendline='%4.4x%4.4x' % (size,nchunk)
        mycrc = crc.one_net_compute_crc(sendline)
        sendline = 'TRANS_START:'+sendline+":%2.2x" % mycrc


        while (rep < 4 and retry):
            rep += 1
            retry = False
            errorstring = 'problems in memload response (TRANS_START crc)'

            self._mgr.send(sendline+"\r")
            self._mgr.popline()
            line=self._mgr.pushline()

            if line.find('The "memload" command failed') >= 0:
                line=self._mgr.popline()
                raise Exception(line)
            if line[:-1] == "0":
                break

            retry = line[:-1] == "1"
            
            if line[:-1] == "2":
                return False

        if ( rep >= 4 and retry):
            raise Exception(errorstring)

        rep = 0
        nch = 0
        mycrc = None
        retry = True
        written = 0

        while (rep < 4 and nch < nchunk):
            rep += 1
            retry = False
            errorstring = 'problems in memdump response (CHUNK crc)'

            towrite = min((written+40,len(self._mem[subset])))
            chunk=self._mem[subset][written:towrite]
            size = (towrite - written)/2

            line='%4.4x%4.4x' % (nch,size)
            mycrc = crc.one_net_compute_crc(chunk)
            line = 'CHUNK_START:'+line+":"+chunk+":%2.2x" % mycrc
            self._mgr.send(line+"\r")
            self._mgr.popline()
            line=self._mgr.pushline()

            if line.find('The "memload" command failed') >= 0:
                line=self._mgr.popline()
                raise Exception(line)

            if line[:-1] == "0":
                nch +=1
                written = towrite
                rep=0
            retry = line[:-1] == "1"
            
            if line[:-1] == "2":
                return False

        if ( rep >= 4 ):
            self._mgr.abort()
            raise Exception(errorstring)

        self._mgr.popline()
        line=self._mgr.pushline()
        return self._mgr._checkok(line)
