#!/bin/bash
HOSTNAME=$(/bin/hostname)
RUNNING=$(/bin/date)
BASHVERSION=$(/bin/bash --version | head -1)
if [ -f /bin/uname ]; then UNAME=$(/bin/uname -srvmpio); else UNAME=$(/usr/bin/uname -v); fi
THECHECK=$(env='() { :;}; echo status=VULNERABLE' bash -c "ls -al /bin/bash" 2>&1 /dev/null)
if [[ $THECHECK == *VULNERABLE* ]] ; then echo "$RUNNING hostname=$HOSTNAME platform=$UNAME cve=2014-6271 status=VULNERABLE version=$BASHVERSION"; else echo "$RUNNING hostname=$HOSTNAME platform=$UNAME cve=2014-6271 status=NOTVULNERABLE version=$BASHVERSION"; fi
