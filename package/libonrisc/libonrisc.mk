#############################################################
#
# libonrisc
#
#############################################################
LIBONRISC_VERSION = 1.4.0
LIBONRISC_SITE = $(call github,visionsystemsgmbh,libonrisc,$(LIBONRISC_VERSION))
LIBONRISC_DEPENDENCIES = libsoc eudev
LIBONRISC_INSTALL_STAGING = YES

$(eval $(cmake-package))

