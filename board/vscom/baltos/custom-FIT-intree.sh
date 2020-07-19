#!/bin/sh

cp $2/board/vscom/baltos/kernel-fit-intree.its $1/
mkimage -f $1/kernel-fit-intree.its $1/kernel-fit.itb
rc=$?
if [ $rc != 0 ]; then
        echo Failed to create kernel-fit.itb
        exit 1
fi

exit 0
