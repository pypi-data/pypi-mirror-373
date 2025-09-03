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
Mail Server Configuration Options
=================================
"""


from tendril.utils.config import ConfigOption
from tendril.utils import log
logger = log.get_logger(__name__, log.DEFAULT)

depends = ['tendril.config.core']


config_elements_mail = [
    ConfigOption(
        'MAIL_USERNAME',
        "None",
        "The username to authenticate with the SMTP server"
    ),
    ConfigOption(
        'MAIL_PASSWORD',
        "None",
        "The password to authenticate with the SMTP server"
    ),
    ConfigOption(
        'MAIL_DEFAULT_SENDER',
        "None",
        "The sender to use when sending emails"
    ),
    ConfigOption(
        'MAIL_SERVER',
        "None",
        "The host of the SMTP server to use"
    ),
    ConfigOption(
        'MAIL_PORT',
        "None",
        "The port of the SMTP server to use"
    ),
    ConfigOption(
        'MAIL_PORT',
        "587",
        "The port of the SMTP server to use"
    ),
    ConfigOption(
        'MAIL_USE_SSL',
        "True",
        "Whether to use SSL when sending emails"
    ),
    ConfigOption(
        'MAIL_USE_TLS',
        "False",
        "Whether to use TLS when sending emails"
    )
]


def load(manager):
    logger.debug("Loading {0}".format(__name__))
    manager.load_elements(config_elements_mail,
                          doc="Tendril E-mail Configuration")
