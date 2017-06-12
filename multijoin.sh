#!/bin/sh

set -x
set -e
#cd /tmp

CTRLCMD=./pyonenetctrl
#CTRLCMD=pyonenetctrl

CHUSER=
#CHUSER=--changeuser

until false 
do 

$CTRLCMD $CHUSER  --master  --client --display --join
$CTRLCMD $CHUSER  --client --master --memdump --insert

#$CTRLCMD $CHUSER  --master  --client --display --join --save
#$CTRLCMD $CHUSER  --master  --client --join
#$CTRLCMD $CHUSER  --master  --client --save

sleep 1

done