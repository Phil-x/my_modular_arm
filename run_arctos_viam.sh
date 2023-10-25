#!/bin/sh

echo  dirname > /home/phil/log/x.txt
echo `dirname $0` >> /home/phil/log/x.txt

cd `dirname $0`
#exec python3 -m my_modular_arm $@
exec python3 -m main $@