#############################################################
#
# libonrisc
#
#############################################################
LIBONRISC_VERSION = 1.8.1
LIBONRISC_SITE = $(call github,visionsystemsgmbh,libonrisc,$(LIBONRISC_VERSION))
LIBONRISC_DEPENDENCIES = libsoc host-pkgconf
LIBONRISC_INSTALL_STAGING = YES
LIBONRISC_SUPPORTS_IN_SOURCE_BUILD = NO

ifeq ($(BR2_PACKAGE_PYTHON)$(BR2_PACKAGE_PYTHON3),y)
	LIBONRISC_DEPENDENCIES += host-swig $(if $(BR2_PACKAGE_PYTHON),python,python3)
	LIBONRISC_CONF_OPTS += -DPYTHON_WRAP=ON -DSWIG_EXECUTABLE=$(SWIG)
else
	LIBONRISC_CONF_OPTS += -DPYTHON_WRAP=OFF
endif

ifeq ($(BR2_PACKAGE_NODEJS),y)
	LIBONRISC_DEPENDENCIES += nodejs
	LIBONRISC_CONF_OPTS += -DNODEJS_WRAP=ON
define LIBONRISC_POST_INSTALL_NODEJS_MODULE
	$(NPM) install -g `$(NPM) pack $(@D)/buildroot-build/nodejs`
	echo "export NODE_PATH=/usr/lib/node_modules" > $(TARGET_DIR)/etc/profile.d/vsnodejs.sh
endef
LIBONRISC_POST_INSTALL_TARGET_HOOKS = LIBONRISC_POST_INSTALL_NODEJS_MODULE
else
	LIBONRISC_CONF_OPTS += -DNODEJS_WRAP=OFF
endif

$(eval $(cmake-package))
