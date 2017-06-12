#!/usr/bin/env python
# -*- coding: utf-8 -*-
# LGPL3. (C) 2017  Paolo Patruno <p.patruno@iperbole.bologna.it>.
#
#                 jsrpc serial communication module
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

import jsrpc
import client_jsrpc as client


class Master(jsrpc.Eval):

    def cmd_change_key(self,key=None):

        return True

    def cmd_invite(self,client):

        return True



    def cmd_remove_device(self,client):

        return True


    def cmd_cancel_invite(self):

        return True

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

