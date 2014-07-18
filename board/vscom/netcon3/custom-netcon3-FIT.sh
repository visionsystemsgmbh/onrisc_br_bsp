#!/bin/sh

cp $2/board/vscom/netcon3/kernel-netcon3.its $1/
mkimage -f $1/kernel-netcon3.its $1/kernel-fit.itb

exit 0
