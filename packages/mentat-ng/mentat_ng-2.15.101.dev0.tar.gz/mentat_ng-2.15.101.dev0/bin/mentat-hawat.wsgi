#-------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------


import hawat

#
# Use prepared factory function to create application instance. The factory
# function takes number of arguments, that can be used to fine tune configuration
# of the application. This is can be very usefull when extending applications`
# capabilities or for purposes of testing. Please refer to the documentation
# for more information.
#
application = hawat.create_app_full(
    config_object = 'hawat.config.ProductionConfig',
    config_file   = '/etc/mentat/mentat-hawat.py.conf',
    config_env    = 'FLASK_CONFIG_FILE'
)

