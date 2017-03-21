#!/bin/sh

cp $2/board/vscom/baltos/kernel-fit.its "${BINARIES_DIR}/"
mkimage -f "${BINARIES_DIR}/kernel-fit.its" "${BINARIES_DIR}/kernel-fit.itb"

exit 0
