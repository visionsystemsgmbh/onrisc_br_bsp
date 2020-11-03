#!/bin/sh

cp $2/board/vscom/baltos/kernel-fit-intree-4.9.its ${BINARIES_DIR}
mkimage -f ${BINARIES_DIR}/kernel-fit-intree-4.9.its ${BINARIES_DIR}/kernel-fit.itb
rc=$?
if [ $rc != 0 ]; then
        echo Failed to create kernel-fit.itb
        exit 1
fi

exit 0
