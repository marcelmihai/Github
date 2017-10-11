#!/bin/bash
HOSTNAME=$(/bin/hostname)
RUNNING=$(/bin/date)
BASHVERSION=$(/bin/bash --version | head -1)
TEMPFILE=$(mktemp -t 7169check.XXXXXX)
MATCH="^bash: findmyvuln: command not found$"

if [ -f /bin/uname ]; then UNAME=$(/bin/uname -srvmpio); else UNAME=$(/usr/bin/uname -v); fi

env X='() { (a)=>\' bash -c "echo findmyvuln > $TEMPFILE" 2>> $TEMPFILE; if [ -f echo ]; then cat echo; fi
THECHECK=$(cat $TEMPFILE)
rm $TEMPFILE
if [ -f echo ]; then rm echo; fi

if [[ $THECHECK =~ $MATCH ]] ; then echo "$RUNNING hostname=$HOSTNAME platform=$UNAME cve=2014-7169 status=VULNERABLE version=$BASHVERSION"; else echo "$RUNNING hostname=$HOSTNAME platform=$UNAME cve=2014-7169 status=NOTVULNERABLE version=$BASHVERSION"; fi

