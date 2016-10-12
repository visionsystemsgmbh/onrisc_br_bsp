#!/bin/sh

cp $2/board/vscom/baltos/kernel-fit-intree.its $1/
mkimage -f $1/kernel-fit-intree.its $1/kernel-fit.itb

exit 0
