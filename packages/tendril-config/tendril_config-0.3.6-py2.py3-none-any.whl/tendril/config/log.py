# Copyright (C) 2022 Chintalagiri Shashank
#
# This file is part of EBS API Server.
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
Logging Configuration Options
=============================
"""


from tendril.utils.config import ConfigOption

import logging
logger = logging.getLogger(__name__)

depends = ['tendril.config.core']


config_elements_log = [
    ConfigOption(
        'LOG_LEVEL', "'INFO'",
        "The logging level to use.",
        parser=logging.getLevelName
    ),
    ConfigOption(
        'JSON_LOGS', "''",
        "Whether to use JSON logging. Applies only to the logfile, and not to the "
        "logs displayed on the console.",
        parser=bool
    ),
    ConfigOption(
        'LOG_PATH', "os.path.join('/var/log', 'tendril', '{}.log'.format(INSTANCE_NAME))",
        "Full path (including filename) to write logs to.",
    ),
    ConfigOption(
        'LOG_COMPACT_TS', 'True',
        "Whether to shorten the timestamp. See LOG_COMPACT_TS_READABLE.",
        parser=bool
    ),
    ConfigOption(
        'LOG_COMPACT_TS_READABLE', 'True',
        "Whether to use a readable format for the compact timestamp. Does not show year and "
        "uses minimal punctuation to keep it short yet readable. If False, shows UNIX "
        "timestamp only, which is even shorter.",
        parser=bool
    ),
    ConfigOption(
        'LOG_COMPACT_SOURCE', 'True',
        "Whether to shorten the source module name.",
        parser=bool
    ),
    ConfigOption(
        'LOG_COMPACT_SOURCE_MAXLEN', '18',
        "Target max length for the source module. Actual length might yet be longer.",
        parser=int
    ),
    ConfigOption(
        'LOG_COMPACT_LEVEL', 'True',
        "Whether to shorten the level name to one letter.",
        parser=bool
    ),
    ConfigOption(
        'LOG_COMPACT_LEVEL_ICON', 'False',
        "Whether to show the level icon instead of the level name. Use only for regular, full "
        "featured terminals. The single letter representation is usually better.",
        parser=bool
    ),
    ConfigOption(
        'LOG_INCLUDE_HOSTNAME', 'False',
        "Whether to include hostname in the log. This is provided to help deal with logs "
        "from multiple replicas or components running in a containerized environment.",
        parser=bool
    ),
    ConfigOption(
        'LOG_HOSTNAME_PREFIX', '""',
        "If set, this prefix is stripped from the hostname and only the remainder is "
        "included in the log message."
    ),
    ConfigOption(
        'LOG_LOGGER_LEVELS', '{}',
        "A dictionary of loggers with custom log levels and the levels "
        "(by level name) to apply."
    )
]


def load(manager):
    logger.debug("Loading {0}".format(__name__))
    manager.load_elements(config_elements_log,
                          doc="Tendril Server Logging Configuration")
    from tendril.utils import log
    log.apply_config(manager)
