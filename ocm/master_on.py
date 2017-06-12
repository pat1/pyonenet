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

import onenet
import client_on as client


class Master(onenet.Eval):

    def cmd_change_key(self,key=None):

        import time

        if key is None:
            key=onenet.rndkey()

        self.sendcmd("change key:"+key)

        self.events.register("change_key", "start")

        line=self._mgr._manageresponse(boards=(self,))

        status = self._change_key_response(line)
        #if status :
        #    self.events.register("change_key", "start")

        return status



    def _change_key_response(self,line):
        """
        return relative,status:
        status=True if no error occours
        """

        if line.find('The "change key" command failed') >= 0:
            self._mgr.popline()
            raise Exception('"The "change key" command failed')

        # here a problem: somtimes this message was read before OK
        terminated=False

        if line.find('Updating NETWORK KEY succeeded') >= 0:
            self._mgr.popline()
            #line=self._mgr._manageresponse(boards=(self,))
            self.events.register("change_key", "SUCCESS")
            terminated=True
            
        status=self._mgr._checkok(line)        
        if status :
            if terminated:
                self.events.register("change_key", "start")
            else:
                self.events.register("change_key", "end","SUCCESS")
        else:
            self.events.register("change_key", "end","FAILED")

        return status


    def cmd_invite(self,client):

        try:
            invitecode=client.ana['invitecode']
        except:
            return False

        self.sendcmd("invite:"+invitecode)

        line=self._mgr._manageresponse((client,))
        status = self._invite_response(line)

        if status:
            self.events.register("invite","start")

        return status


    def _invite_response(self,line):
        """
        return relative,status:
        relative=True if message is change_key relative
        status=True if no error occours
        """

        if line.find('The "invite" command failed') >= 0:
            self._mgr.popline()
            raise Exception('The "invite" command failed')
        
        return self._mgr._checkok(line)        


    def cmd_remove_device(self,client):

        if client.ana["status"] == "Not joined." :
            return False
            
        try:
            did=client.ana['did']
        except:
            return False

        self.sendcmd("remove device:%03X" % did)

        line=self._mgr._manageresponse((client,))
        print "uno",line
        status = self._remove_device_response(line)

        if status:
            self.events.register("remove device","start")

        return status


    def _remove_device_response(self,line):
        """
        status=True if no error occours
        """

        if line.find('The "remove device" command failed') >= 0:
            self._mgr.popline()
            print "ciao"
            raise Exception(line)


        #ocm-m> Deleting did 006.  First removing all relevant peer assignments to did 006.
        print "due"
        if line.find('Deleting did ') >= 0:
            if line.find('First removing all relevant peer assignments to did') >= 0 :
                print "tre"
                self._mgr.popline()
            
        line=self._mgr._manageresponse((client,))
        return self._mgr._checkok(line)        


    def cmd_cancel_invite(self):

        self.sendcmd("cancel invite")
        line=self._mgr._manageresponse()
        return self._cancel_invite_response(line)


    def _cancel_invite_response(self,line):
        """
        return relative,status:
        relative=True if message is change_key relative
        status=True if no error occours
        """

        if line.find('The "cancel invite" command failed') >= 0:
            self._mgr.popline()
            raise Exception('The "cancel invite" command failed')
        
        return self._mgr._checkok(line)        


def mainn():

    m=Master(device="/dev/ttyUSB0")
    #print m.ana

    c=Client.client(device="/dev/ttyUSB1")
    #c=Client.client(did="003")
    #print c.ana

    print "master; cmd erase;  torna:",m.cmd_erase()
    print "client; cmd erase;  torna:",c.cmd_erase()

    #print "master; cmd setni;  torna:",m.cmd_setni("001002868","2325-8247")
    #print "client; cmd setni;  torna:",c.cmd_setni("001002867","2325-2384")

    print "cmd channel;  torna:",m.cmd_channel(region="US",chan=1)
    #print "cmd channel;  torna:",m.cmd_channel(region="EUR",chan=1)
    #print "cmd list; torna:",m.cmd_list()
    #print m.ana

    #print "cmd channel;  torna:",c.cmd_channel(region="EUR",chan=2)
    #print "cmd list; torna:",c.cmd_list()
    #print c.ana

    print "cmd change key;  torna:",m.cmd_change_key()
    #print "cmd list;  torna:",m.cmd_list()

    print "async change key; torna:",m.wait(m,"change_key",10)

    print "join; torna:", c.cmd_join()
    print "invite; torna:", m.cmd_invite(c)

    print "async invite: torna:",m.wait(m,"invite",30)

    #while not m.wait(m,"invite",30):
    #    print "cancel invite; torna:", m.cmd_cancel_invite(c)
    #    print "invite; torna:", m.cmd_invite(c)
    #    print "join; torna:", c.cmd_join()


    #print "cmd list;  torna:",m.cmd_list()
    #print m.ana
    #print "cmd list;  torna:",c.cmd_list()
    #print c.ana

    m.cmd_save()
    c.cmd_save()

    print "creato un client con did:",c.ana["did"]

    c.close()
    m.close()

def main():


    m=Master(device="/dev/ttyUSB0")
    #c=client.Client(device="/dev/ttyUSB1")
    c=client.Client(did=4)

    print "master; cmd single 1 on;   torna:",m.cmd_single(c,srcunit=0,dstunit=1,onoff=1)
    print "master; cmd single 0 on;   torna:",m.cmd_single(c,srcunit=0,dstunit=0,onoff=1)
    print "master; cmd single 1 off;  torna:",m.cmd_single(c,srcunit=0,dstunit=1,onoff=0)
    print "master; cmd single 0 off;  torna:",m.cmd_single(c,srcunit=0,dstunit=0,onoff=0)



    for i in range(9):
        of=i%2
        print "master; cmd single;  torna:",m.cmd_single(c,srcunit=0,dstunit=0,onoff=of)

    import time
    for i in range(9):
        of=i%2
        print "master; cmd single;  torna:",m.cmd_single(c,srcunit=0,dstunit=1,onoff=of)
        time.sleep(1)

    m.receive((m,c),1)


    c.close()
    m.close()


if __name__ == '__main__':
    main()  # (this code was run as script)

