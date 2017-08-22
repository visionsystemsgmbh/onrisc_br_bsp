#############################################################
#
# libonrisc
#
#############################################################
LIBONRISC_VERSION = 1.5.4
LIBONRISC_SITE = $(call github,visionsystemsgmbh,libonrisc,$(LIBONRISC_VERSION))
LIBONRISC_DEPENDENCIES = libsoc eudev host-pkgconf
LIBONRISC_INSTALL_STAGING = YES

ifeq ($(BR2_PACKAGE_PYTHON)$(BR2_PACKAGE_PYTHON3),y)
	LIBONRISC_DEPENDENCIES += host-swig $(if $(BR2_PACKAGE_PYTHON),python,python3)
	LIBONRISC_CONF_OPTS += -DPYTHON_WRAP=ON -DSWIG_EXECUTABLE=$(SWIG)
else
	LIBONRISC_CONF_OPTS += -DPYTHON_WRAP=OFF
endif

$(eval $(cmake-package))
