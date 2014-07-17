OnRISC Buildroot based BSP
==========================

Installation
------------

1. git clone https://github.com/yegorich/onrisc_br_bsp.git
2. git clone http://git.buildroot.net/git/buildroot.git
3. cd buildroot
4. make BR2_EXTERNAL=../onrisc_br_bsp/ help

Now you can choose a default config for desired device. For example Balios:

make balios_defconfig

Invoking make would compile the whole set of images from bootloader till root file system.
