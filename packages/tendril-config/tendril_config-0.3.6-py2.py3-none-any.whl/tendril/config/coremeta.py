# Copyright (C) 2019 Chintalagiri Shashank
#
# This file is part of Tendril.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Core Metadata Configuration Options
===================================
"""


from tendril.utils.config import ConfigOption
from tendril.utils import log
logger = log.get_logger(__name__, log.DEFAULT)

depends = ['tendril.config.core']


config_elements_coremeta = [
    ConfigOption(
        'COMPONENT_NAME',
        "''",
        "Name of the component. To be used for log generation and identification "
        "of source component on platform level artefacts."
    ),
    ConfigOption(
        'ADMIN_FULLNAME',
        "''",
        "Instance Administrator Name"
    ),
    ConfigOption(
        'ADMIN_EMAIL',
        "''",
        "Instance Administrator E-mail Address"
    ),
    ConfigOption(
        'INSTANCE_SOURCES',
        '"https://github.com/tendril-framework"',
        'The location of the sources of the tendril code used by the instance'
    ),
    ConfigOption(
        'INSTANCE_FOLDER_SOURCES',
        '"https://github.com/tendril-framework/tendril-instance-cookiecutter"',
        'The location of the sources of the tendril instance folder used by '
        'the instance'
    ),
    ConfigOption(
        'INSTANCE_DOCUMENTATION_PATH',
        '"http://tendril.chintal.in/doc"',
        "The location of the documentation related to the instance"
    ),
]


def load(manager):
    logger.debug("Loading {0}".format(__name__))
    manager.load_elements(config_elements_coremeta,
                          doc="Tendril Core Metadata Configuration")
