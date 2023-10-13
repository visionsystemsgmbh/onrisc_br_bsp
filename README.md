OnRISC Buildroot based BSP
==========================

Installation
------------

OnRISC BSP requires Buildroot version 2032.08 or newer.

1. git clone https://github.com/visionsystemsgmbh/onrisc_br_bsp.git
2. git clone https://git.buildroot.net/buildroot
3. cd buildroot
4. git checkout 2023.08.x
5. make BR2_EXTERNAL=../onrisc_br_bsp/ list-defconfigs

Now you can choose a default config for desired device. For example Baltos:

make baltos_defconfig

Invoking make would compile the whole set of images from bootloader till root file system. You'll find binaries under `output/images` folder.

Related Links
-------------
* Buildroot documentation: http://nightly.buildroot.org/manual.html
* Device Tree slides: http://events.linuxfoundation.org/sites/events/files/slides/petazzoni-device-tree-dummies.pdf
* Flattened Image Tree slides: http://elinux.org/images/f/f4/Elc2013_Fernandes.pdf 
