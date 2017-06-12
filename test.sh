#!/bin/sh

set -x
set +e
#cd /tmp

CTRLCMD=./pyonenetctrl
#CTRLCMD=pyonenetctrl

CHUSER=
#CHUSER=--changeuser

until false 
do 
$CTRLCMD $CHUSER  --master --client --single --pinnumber=0 --pinonoff=0 --did=2
$CTRLCMD $CHUSER  --master --client --single --pinnumber=1 --pinonoff=0 --did=2
$CTRLCMD $CHUSER  --master --client --single --pinnumber=0 --pinonoff=1 --did=2
$CTRLCMD $CHUSER  --master --client --single --pinnumber=1 --pinonoff=1 --did=2
#$CTRLCMD $CHUSER  --master  --client --client --display

sleep 1

done