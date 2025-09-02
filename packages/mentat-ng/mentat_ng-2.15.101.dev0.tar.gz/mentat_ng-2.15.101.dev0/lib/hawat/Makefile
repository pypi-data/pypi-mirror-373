#-------------------------------------------------------------------------------
# MASTER MAKEFILE FOR MENTAT-NG PROJECT
#
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Author: Jan Mach <jan.mach@cesnet.cz>
# Use of this source is governed by an MIT license, see LICENSE file.
#-------------------------------------------------------------------------------


#
# Default make target, alias for 'help', you must explicitly choose the target.
#
default: help


#===============================================================================


PYBABEL = pybabel

DIR_LIB       = ..
DIR_LIB_HAWAT = .

DIR_TEMPLATES_INFORMANT ?= /etc/mentat/templates/informant
DIR_TEMPLATES_REPORTER  ?= /etc/mentat/templates/reporter
DIR_TEMPLATES_UTEST     ?= /etc/mentat/templates/utest

TMP_BABEL_CONF = /tmp/babel_tmp.cfg

#
# Include common makefile configurations.
#
include Makefile.inc


#===============================================================================


#
# Display extensive help information page.
#
help:
	@echo ""
	@echo "                 ███╗   ███╗███████╗███╗   ██╗████████╗ █████╗ ████████╗"
	@echo "                 ████╗ ████║██╔════╝████╗  ██║╚══██╔══╝██╔══██╗╚══██╔══╝"
	@echo "                 ██╔████╔██║█████╗  ██╔██╗ ██║   ██║   ███████║   ██║"
	@echo "                 ██║╚██╔╝██║██╔══╝  ██║╚██╗██║   ██║   ██╔══██║   ██║"
	@echo "                 ██║ ╚═╝ ██║███████╗██║ ╚████║   ██║   ██║  ██║   ██║"
	@echo "                 ╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝"
	@echo "                        $(FAINT)Copyright (C) since 2011 CESNET, z.s.p.o$(NC)"
	@echo ""
	@echo " $(GREEN)$(BOLD)╔══════════════════════════════════════════════════════════════════════════════════╗$(NC)"
	@echo " $(GREEN)$(BOLD)║                          LIST OF AVAILABLE MAKE TARGETS                          ║$(NC)"
	@echo " $(GREEN)$(BOLD)╚══════════════════════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "  * $(GREEN)pybabel-patch$(NC): patch babel library"
	@echo "  * ${GREEN}hpybabel-init INIT_LOCALE=lc${NC}: extract and init Hawat translations for given locale $(FAINT)lc$(NC)"
	@echo "  * $(GREEN)hpybabel-update$(NC): extract and update Hawat translations"
	@echo "  * $(GREEN)hpybabel-compile$(NC): compile Hawat translations"
	@echo "  * ${GREEN}mpybabel-init INIT_LOCALE=lc${NC}: extract and init Mentat translations for given locale $(FAINT)lc$(NC)"
	@echo "  * $(GREEN)mpybabel-update$(NC): extract and update Mentat translations"
	@echo "  * $(GREEN)mpybabel-compile$(NC): compile Mentat translations"
	@echo "  * $(GREEN)translations-compile$(NC): compile all available translations"
	@echo ""
	@echo " $(GREEN)════════════════════════════════════════════════════════════════════════════════════$(NC)"
	@echo ""


#-------------------------------------------------------------------------------

# Babel does not support paths containing parent directory (..) in mapping files.
# Because of that if you need path including directories higher in tree that your pwd you need the root.
# So babel.cfg located in mentat components are templates that are filled with absolute paths to its respective jinja files and python files in mentat packages.
# cut is used to remove slash from begging of path returned by realpath because babel needs path as relative to its input directory.
#
# Alternative solution that uses the hawat-cli utility:
#   APP_ROOT_PATH=$(shell realpath ./chroot) hawat-cli intl init $(INIT_LOCALE)
#
hpybabel-init:
	@echo "\n$(GREEN)*** Initializing translations for new locale for Hawat user interface ***$(NC)\n"
	@echo "Locale name: $(INIT_LOCALE)"
	@$(PYBABEL) extract -F $(DIR_LIB_HAWAT)/babel.cfg -o $(DIR_LIB_HAWAT)/messages.pot -k lazy_gettext -k tr_ $(DIR_LIB)
	@cat $(DIR_TEMPLATES_REPORTER)/babel.cfg | sed -e 's,{DIR_LIB},$(shell realpath ${DIR_LIB} | cut -c2-),g' -e 's,{DIR_TEMPLATES_REPORTER},$(shell realpath ${DIR_TEMPLATES_REPORTER} | cut -c2-),g' > $(TMP_BABEL_CONF)
	$(PYBABEL) extract -F $(TMP_BABEL_CONF) -o $(DIR_TEMPLATES_REPORTER)/messages.pot -k lazy_gettext -k tr_ --no-location /
	@rm $(TMP_BABEL_CONF)
	@$(PYBABEL) init -i $(DIR_LIB_HAWAT)/messages.pot -d $(DIR_LIB_HAWAT)/translations -l $(INIT_LOCALE)
	@$(PYBABEL) init -i $(DIR_TEMPLATES_REPORTER)/messages.pot -d $(DIR_TEMPLATES_REPORTER)/translations -l $(INIT_LOCALE)

#
# Alternative solution that uses the hawat-cli utility:
#   APP_ROOT_PATH=$(shell realpath ./chroot) hawat-cli intl update
#
hpybabel-update:
	@echo "\n$(GREEN)*** Updating translations for Hawat user interface ***$(NC) $(DIR_LIB_HAWAT)\n"
	@$(PYBABEL) extract -F $(DIR_LIB_HAWAT)/babel.cfg -o $(DIR_LIB_HAWAT)/messages.pot -k lazy_gettext -k tr_ $(DIR_LIB)
	@cat $(DIR_TEMPLATES_REPORTER)/babel.cfg | sed -e 's,{DIR_LIB},$(shell realpath ${DIR_LIB} | cut -c2-),g' -e 's,{DIR_TEMPLATES_REPORTER},$(shell realpath ${DIR_TEMPLATES_REPORTER} | cut -c2-),g' > $(TMP_BABEL_CONF)
	@$(PYBABEL) extract -F $(TMP_BABEL_CONF) -o $(DIR_TEMPLATES_REPORTER)/messages.pot -k lazy_gettext -k tr_ --no-location /
	@rm $(TMP_BABEL_CONF)
	@$(PYBABEL) update -i $(DIR_LIB_HAWAT)/messages.pot -d $(DIR_LIB_HAWAT)/translations
	@$(PYBABEL) update -i $(DIR_TEMPLATES_REPORTER)/messages.pot -d $(DIR_TEMPLATES_REPORTER)/translations

#
# Alternative solution that uses the hawat-cli utility:
#   APP_ROOT_PATH=$(shell realpath ./chroot) hawat-cli intl compile
#
hpybabel-compile:
	@echo "\n$(GREEN)*** Compiling translations for Hawat user interface ***$(NC)\n"
	@$(PYBABEL) compile -d $(DIR_LIB_HAWAT)/translations
	@$(PYBABEL) compile -d $(DIR_TEMPLATES_REPORTER)/translations

mpybabel-init:
	@echo "\n$(GREEN)*** Initializing translations for new locale for Mentat ***$(NC)\n"
	@echo "Locale name: $(INIT_LOCALE)"
	@cat $(DIR_TEMPLATES_INFORMANT)/babel.cfg | sed -e 's,{DIR_LIB},$(shell realpath ${DIR_LIB} | cut -c2-),g' -e 's,{DIR_TEMPLATES_INFORMANT},$(shell realpath ${DIR_TEMPLATES_INFORMANT} | cut -c2-),g' > $(TMP_BABEL_CONF)
	@$(PYBABEL) extract -F $(TMP_BABEL_CONF) -o $(DIR_TEMPLATES_INFORMANT)/messages.pot -k lazy_gettext -k tr_ --no-location /
	@cat $(DIR_TEMPLATES_REPORTER)/babel.cfg | sed -e 's,{DIR_LIB},$(shell realpath ${DIR_LIB} | cut -c2-),g' -e 's,{DIR_TEMPLATES_REPORTER},$(shell realpath ${DIR_TEMPLATES_REPORTER} | cut -c2-),g' > $(TMP_BABEL_CONF)
	@$(PYBABEL) extract -F $(TMP_BABEL_CONF) -o $(DIR_TEMPLATES_REPORTER)/messages.pot -k lazy_gettext -k tr_ --no-location /
	@cat $(DIR_TEMPLATES_UTEST)/babel.cfg | sed -e 's,{DIR_LIB},$(shell realpath ${DIR_LIB} | cut -c2-),g' -e 's,{DIR_TEMPLATES_UTEST},$(shell realpath ${DIR_TEMPLATES_UTEST} | cut -c2-),g' > $(TMP_BABEL_CONF)
	@$(PYBABEL) extract -F $(TMP_BABEL_CONF) -o $(DIR_TEMPLATES_UTEST)/messages.pot -k lazy_gettext -k tr_ --no-location /
	@$(PYBABEL) init -i $(DIR_TEMPLATES_INFORMANT)/messages.pot -d $(DIR_TEMPLATES_INFORMANT)/translations -l $(INIT_LOCALE)
	@$(PYBABEL) init -i $(DIR_TEMPLATES_REPORTER)/messages.pot -d $(DIR_TEMPLATES_REPORTER)/translations -l $(INIT_LOCALE)
	@$(PYBABEL) init -i $(DIR_TEMPLATES_UTEST)/messages.pot -d $(DIR_TEMPLATES_UTEST)/translations -l $(INIT_LOCALE)
	@rm $(TMP_BABEL_CONF)

mpybabel-update:
	@echo "\n$(GREEN)*** Updating translations for Mentat ***$(NC)\n"
	@cat $(DIR_TEMPLATES_INFORMANT)/babel.cfg | sed -e 's,{DIR_LIB},$(shell realpath ${DIR_LIB} | cut -c2-),g' -e 's,{DIR_TEMPLATES_INFORMANT},$(shell realpath ${DIR_TEMPLATES_INFORMANT} | cut -c2-),g' > $(TMP_BABEL_CONF)
	@$(PYBABEL) extract -F $(TMP_BABEL_CONF) -o $(DIR_TEMPLATES_INFORMANT)/messages.pot -k lazy_gettext -k tr_ --no-location /
	@cat $(DIR_TEMPLATES_REPORTER)/babel.cfg | sed -e 's,{DIR_LIB},$(shell realpath ${DIR_LIB} | cut -c2-),g' -e 's,{DIR_TEMPLATES_REPORTER},$(shell realpath ${DIR_TEMPLATES_REPORTER} | cut -c2-),g' > $(TMP_BABEL_CONF)
	@$(PYBABEL) extract -F $(TMP_BABEL_CONF) -o $(DIR_TEMPLATES_REPORTER)/messages.pot -k lazy_gettext -k tr_ --no-location /
	@cat $(DIR_TEMPLATES_UTEST)/babel.cfg | sed -e 's,{DIR_LIB},$(shell realpath ${DIR_LIB} | cut -c2-),g' -e 's,{DIR_TEMPLATES_UTEST},$(shell realpath ${DIR_TEMPLATES_UTEST} | cut -c2-),g' > $(TMP_BABEL_CONF)
	@$(PYBABEL) extract -F $(TMP_BABEL_CONF) -o $(DIR_TEMPLATES_UTEST)/messages.pot -k lazy_gettext -k tr_ --no-location /
	@$(PYBABEL) update -i $(DIR_TEMPLATES_INFORMANT)/messages.pot -d $(DIR_TEMPLATES_INFORMANT)/translations
	@$(PYBABEL) update -i $(DIR_TEMPLATES_REPORTER)/messages.pot -d $(DIR_TEMPLATES_REPORTER)/translations
	@$(PYBABEL) update -i $(DIR_TEMPLATES_UTEST)/messages.pot -d $(DIR_TEMPLATES_UTEST)/translations
	@rm $(TMP_BABEL_CONF)

mpybabel-compile:
	@echo "\n$(GREEN)*** Compiling translations for Mentat ***$(NC)\n"
	@$(PYBABEL) compile -d $(DIR_TEMPLATES_INFORMANT)/translations --statistics
	@$(PYBABEL) compile -d $(DIR_TEMPLATES_REPORTER)/translations --statistics
	@$(PYBABEL) compile -d $(DIR_TEMPLATES_UTEST)/translations --statistics

#
# Compile all available translations.
#
translations-compile: hpybabel-compile mpybabel-compile


# Empty rule as dependency will force make to always perform target
# Source: https://www.gnu.org/software/make/manual/html_node/Force-Targets.html
FORCE:
