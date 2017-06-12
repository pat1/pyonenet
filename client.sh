#!/bin/sh

set -x
set -e
#cd /tmp

#NID=$1
NID=123456789
#INVITECODE=$1
INVITECODE=2223

CTRLCMD=./pyonenetctrl
#CTRLCMD=pyonenetctrl

CHUSER=
#CHUSER=--changeuser

$CTRLCMD $CHUSER  --client --display

$CTRLCMD $CHUSER  --client --erase
sleep 2

set +e
$CTRLCMD $CHUSER  --client --nid=$NID --invitecode=2222-$INVITECODE --setni
set -e

sleep 2
$CTRLCMD $CHUSER  --client --pinnumber=0 --pinstate=output
$CTRLCMD $CHUSER  --client --pinnumber=1 --pinstate=output
$CTRLCMD $CHUSER  --client --pinnumber=2 --pinstate=input
$CTRLCMD $CHUSER  --client --pinnumber=3 --pinstate=input

$CTRLCMD $CHUSER  --client --save

