#!/bin/bash
cd `dirname $0`
. bin/activate
python rax-nextgen-notify.py
exit $?
