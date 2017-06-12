#!/usr/bin/env python
# -*- coding: utf-8 -*-
# LGPL3. (C) 2011 Paolo Patruno <p.patruno@iperbole.bologna.it>.
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

def composebyte(data):
    """
    iterator to decompose a hex string
    data is an hex string
    return hex for one byte or the odd digit if there is
    """
    cc=""

    for c in data:
        if len(cc) == 2:
            cc=""
        if len(cc) == 0:
            cc=c
        else:
            cc+=c
                
        if len(cc) == 2:
            yield cc

    if len(cc) == 1:
        yield cc

def one_net_compute_crc(data,starting_crc=0XFF,order=8):
    """
    compute crc like one-net C code
    """
    polynom = 0x00A6
    mask = 0x00FF
    crc_high_bit = 0X01 << (order - 1)
    crc=starting_crc

    for c in composebyte(data):

        j=0x80
        while(j >0 ):
            #print j,c

            bit = crc & crc_high_bit
            crc <<= 1
            crc &= 0XFFFF

            if(int(c,16) & j):
                bit ^= crc_high_bit
                bit &= 0XFFFF
            if(bit):
                crc ^= polynom
                crc &= 0XFFFF
            j >>= 1

        c=""
    return (crc & mask) & 0XFFFF


def main():
    """
    this is an example to use this module
    """

    print hex(one_net_compute_crc('E0030C0D0E0F76A0249B05D816C594F66EC4DE315'))
    print "the expected crc was hex 44"


if __name__ == '__main__':
    main()  # (this code was run as script)
