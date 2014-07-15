#!/bin/sh

cp $2/board/vscom/balios/kernel-fit-balios-ir5221.its $1/
mkimage -f $1/kernel-fit-balios-ir5221.its $1/kernel-fit-balios-ir5221.itb

exit 0
