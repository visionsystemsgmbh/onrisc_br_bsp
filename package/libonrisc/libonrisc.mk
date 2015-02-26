#############################################################
#
# libonrisc
#
#############################################################
LIBONRISC_VERSION = 1.4.1
LIBONRISC_SITE = $(call github,visionsystemsgmbh,libonrisc,$(LIBONRISC_VERSION))
LIBONRISC_DEPENDENCIES = libsoc eudev
LIBONRISC_INSTALL_STAGING = YES

ifeq ($(BR2_PACKAGE_LIBONRISC_PYTHON_WRAPPER),y)
	LIBONRISC_CONF_OPTS += -DPYTHON_WRAP=ON
else
	LIBONRISC_CONF_OPTS += -DPYTHON_WRAP=OFF
endif

$(eval $(cmake-package))

