#!/bin/sh

set -x
set -e
#cd /tmp

CTRLCMD=./pyonenetctrl
#CTRLCMD=pyonenetctrl

CHUSER=
#CHUSER=--changeuser

$CTRLCMD $CHUSER  --master --display

$CTRLCMD $CHUSER  --master  --erase
sleep 2
set +e
$CTRLCMD $CHUSER  --master --nid=123456789  --invitecode=2222-2222 --setni 

#001002868 

set -e
sleep 2
$CTRLCMD $CHUSER  --master --region=EUR --channel=1
sleep 5

$CTRLCMD $CHUSER  --master --changekey
$CTRLCMD $CHUSER  --master --changekey
$CTRLCMD $CHUSER  --master --changekey
$CTRLCMD $CHUSER  --master --changekey --save

#echo ""
#echo "warning"
#echo "RESET THE BOARD now !!!! "
