#############################################################
#
# node-red-contrib-libonrisc
#
#############################################################
NODE_RED_CONTRIB_LIBONRISC_VERSION = 1.0.0
NODE_RED_CONTRIB_LIBONRISC_SITE = $(call github,visionsystemsgmbh,node-red-contrib-libonrisc,$(NODE_RED_CONTRIB_LIBONRISC_VERSION))
NODE_RED_CONTRIB_LIBONRISC_DEPENDENCIES = libonrisc nodejs

define NODE_RED_CONTRIB_LIBONRISC_POST_INSTALL_NODEJS_MODULE
	$(NPM) install -g `$(NPM) pack $(@D)`
endef
NODE_RED_CONTRIB_LIBONRISC_POST_INSTALL_TARGET_HOOKS = NODE_RED_CONTRIB_LIBONRISC_POST_INSTALL_NODEJS_MODULE

$(eval $(generic-package))
