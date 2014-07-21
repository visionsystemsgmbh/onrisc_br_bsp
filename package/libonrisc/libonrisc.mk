#############################################################
#
# libonrisc
#
#############################################################
LIBONRISC_VERSION = 1.1.0
LIBONRISC_SITE = $(call github,yegorich,libonrisc,$(LIBONRISC_VERSION))
LIBONRISC_DEPENDENCIES = libsoc
LIBONRISC_INSTALL_STAGING = YES

$(eval $(cmake-package))

