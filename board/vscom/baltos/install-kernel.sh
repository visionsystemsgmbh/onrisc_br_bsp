#!/bin/sh

mkdir -p $1/boot
cp "${BINARIES_DIR}/kernel-fit.itb" $1/boot

exit 0
