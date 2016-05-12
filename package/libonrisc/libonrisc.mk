#############################################################
#
# libonrisc
#
#############################################################
LIBONRISC_VERSION = 1.5.2
LIBONRISC_SITE = $(call github,visionsystemsgmbh,libonrisc,$(LIBONRISC_VERSION))
LIBONRISC_DEPENDENCIES = libsoc eudev host-pkgconf
LIBONRISC_INSTALL_STAGING = YES

ifeq ($(BR2_PACKAGE_LIBONRISC_PYTHON_WRAPPER),y)
	LIBONRISC_DEPENDENCIES += host-swig
	LIBONRISC_CONF_OPTS += -DPYTHON_WRAP=ON -DSWIG_EXECUTABLE=$(SWIG)
else
	LIBONRISC_CONF_OPTS += -DPYTHON_WRAP=OFF
endif

$(eval $(cmake-package))
