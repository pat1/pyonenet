#!/bin/sh

set -x
set -e
#cd /tmp

CTRLCMD=./pyonenetctrl
#CTRLCMD=pyonenetctrl

CHUSER=
#CHUSER=--changeuser

$CTRLCMD  $CHUSER --master --client --join --save --insert --insertmaster


