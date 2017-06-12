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

import serial 
import time
import onenet
import master_on as master


class Client(onenet.Eval):


    def cmd_join(self,timeout=60,region="EUR",chan=1):

        self.sendcmd("join:%d:%s:%d"%(timeout,region,chan))
        line=self._mgr._manageresponse((self,))

        status = self._join_response(line)
        if status:
            self.events.register("join","start")
        return status


    def _join_response(self,line):
        """
        status=True if no error occours
        """

        if line.find('The "join" command failed') >= 0:
            self._mgr.popline()
            raise Exception('The "join" command failed')
        return self._mgr._checkok(line)


def main():

    #print "init"
    c=Client(device="/dev/ttyUSB1")
#    c=client(client=4)

    print "canale 1; torna:",c.channel(region="EUR",chan=1)
    c.list()
    print c.ana

    print "canale 2; torna:",c.channel(region="EUR",chan=2)
    c.list()
    print c.ana

    c.close()


if __name__ == '__main__':
    main()  # (this code was run as script)

