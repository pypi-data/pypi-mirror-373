# Copyright (C) 2015 Chintalagiri Shashank
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
The Config Module (:mod:`tendril.config.legacy`)
================================================

This module provides the core configuration for Tendril.

The Tendril configuration file is itself a Python file, and is imported
from it's default location (``INSTANCE_ROOT/instance_config.py``, where
INSTANCE_ROOT is ``~/.tendril``). In case this folder needs to be moved
elsewhere, such as when it needs to be run via wsgi using the web server's
user, the INSTANCE_ROOT can be moved by placing a file in the user's
home directory (``~/.tendril/redirect``), containing the path to the
actual instance folder.

The ``instance_config.py`` file is the primary configuration for Tendril.
It is intended to be maintained at an Instance level by the tendril
administrator. Since some parameters may need to be changed per-installation
to adapt it to the user's setup, an additional configuration file can be
added in (``INSTANCE_ROOT/local_config_overrides.py``), containing only those
parameters which the user wishes to override.

When the configuration is parsed during startup, (at the time of the first
import of the config module) this module performs the import using the
:func:`tendril.utils.fsutils.import_` function and the :mod:`imp` module.
Each recognized config option and variable is obtained from the first
location where it is found from the following list of sources:

    - ``local_config_overrides.py``
    - ``instance_config.py``
    - The defaults specified here.

The following constraints should be kept in mind when setting up your
configuration :

    - The configuration files are all python files. You can execute pretty
      much whatever you want within them, as long as the final configuration
      value ends up in the module namespace at the correct variable.
    - The order of the config parameters is somewhat important. The actual
      configuration values can be constructed at run time from
      configurations parameters which already exist in the namespace.
    - The core config module (this one) uses ``eval()`` to execute the
      ``default`` strings. The values in ``instance_config`` and
      ``local_config_overrides``, however, are used as is. As such, each
      option or constant specified in one of those files must be fully
      specified within that file - it can't, for instance, use the
      INSTANCE_ROOT value to construct paths unless it defines it for
      itself.
    - Configuration constants will be set in the instance and local config
      modules. Configuration options will not.

Configuration Options
---------------------

.. documentedlist::
    :listobject: tendril.config.legacy.all_config_option_groups
    :header: Option Default Description
    :spantolast:
    :descend:


Configuration Constants
-----------------------

.. documentedlist::
    :listobject: tendril.config.legacy.all_config_constant_groups
    :header: Option Default Description
    :spantolast:
    :descend:

"""

from __future__ import print_function

import os
import sys
import inspect

from tendril.utils.fsutils import import_

config_module = sys.modules[__name__]
CONFIG_PATH = os.path.abspath(inspect.getfile(inspect.currentframe()))


class ConfigConstant(object):
    """
    A configuration `constant`. This is fully specified in this
    file and cannot be changed by the user or the instance
    administrator without modifying the core code.

    The value itself is constructed using ``eval()``.
    """
    def __init__(self, name, default, doc):
        self.name = name
        self.default = default
        self.doc = doc

    @property
    def value(self):
        return eval(self.default)


def load_constants(constants):
    """
    Loads the constants in the provided list into the module
    namespace.

    :param constants: list of :class:`ConfigConstant`
    :return: None
    """
    for option in constants:
        setattr(config_module, option.name, option.value)


config_constants_basic = [
    ConfigConstant(
        'TENDRIL_ROOT',
        'os.path.normpath(os.path.join(CONFIG_PATH, os.pardir, os.pardir))',
        'DEPRECATED. Path to the tendril package root.'
    ),
    ConfigConstant(
        'INSTANCE_ROOT',
        "os.path.join(os.path.expanduser('~'), '.tendril')",
        "Path to the tendril instance root. Can be redirected if necessary"
        "with a file named ``redirect`` in this folder."
    )
]

load_constants(config_constants_basic)


if os.path.exists(os.path.join(INSTANCE_ROOT, 'redirect')):
    print("Found redirect")
    with open(os.path.join(INSTANCE_ROOT, 'redirect'), 'r') as f:
        INSTANCE_ROOT = f.read().strip()


config_constants_redirected = [
    ConfigConstant(
        'INSTANCE_CONFIG_FILE',
        "os.path.join(INSTANCE_ROOT, 'instance_config.py')",
        'Path to the tendril instance configuration.'
    ),
    ConfigConstant(
        'LOCAL_CONFIG_FILE',
        "os.path.join(INSTANCE_ROOT, 'local_config_overrides.py')",
        'Path to local overrides to the instance configuration.'
    ),
]

load_constants(config_constants_redirected)

if os.path.exists(INSTANCE_CONFIG_FILE):
    INSTANCE_CONFIG = import_(INSTANCE_CONFIG_FILE)
else:
    INSTANCE_CONFIG = {}

if os.path.exists(LOCAL_CONFIG_FILE):
    LOCAL_CONFIG = import_(LOCAL_CONFIG_FILE)
else:
    LOCAL_CONFIG = {}


class ConfigOption(object):
    """
    A configuration `option`. These options can be overridden
    by specifying them in the ``instance_config`` and
    ``local_config_overrides`` files.

    If specified in one of those files, the value should be
    the actual configuration value and not an expression. The
    default value specified here is used through ``eval()``.

    """
    def __init__(self, name, default, doc):
        self.name = name
        self.default = default
        self.doc = doc

    @property
    def value(self):
        try:
            return getattr(LOCAL_CONFIG, self.name)
        except AttributeError:
            pass
        try:
            return getattr(INSTANCE_CONFIG, self.name)
        except AttributeError:
            try:
                return eval(self.default)
            except SyntaxError:
                print("Required config option not set in "
                      "instance config : " + self.name)
                raise


def load_config(options):
    """
    Loads the options in the provided list into the module
    namespace.

    :param options: list of :class:`ConfigOption`
    :return: None
    """
    for option in options:
        setattr(config_module, option.name, option.value)


config_options_paths = [
    ConfigOption(
        'AUDIT_PATH',
        "os.path.join(INSTANCE_ROOT, 'manual-audit')",
        "Folder where files generated for manual audit should be stored"
    ),
    ConfigOption(
        'INSTANCE_CACHE',
        "os.path.join(INSTANCE_ROOT, 'cache')",
        "Folder within which the tendril instance should store it's cache(s)."
        "Make sure the the users running tendril (as well as the webserver, "
        "if the web frontend is being used) have write access to this folder."
    ),
    ConfigOption(
        'SVN_ROOT',
        "os.path.join(INSTANCE_ROOT, 'projects')",
        "Common ancestor for all VCS checkout folders. While tendril will "
        "try to descend into this folder indefinitely, avoid using overly "
        "generic paths (like '/' or '~') to avoid surprises and preserve "
        "performance."
    ),
    ConfigOption(
        'PROJECTS_ROOT',
        "SVN_ROOT",
        "Common ancestor for all project folders. Use this if your projects"
        "are in a single sub-tree of your VCS_ROOT, for example. \nWhile "
        "tendril will try to descend into this folder indefinitely, avoid "
        "using overly generic paths (like '/' or '~') to avoid surprises "
        "and preserve performance."
    ),
]

load_config(config_options_paths)


config_options_fs = [
    ConfigOption(
        'DOCSTORE_ROOT',
        "os.path.join(INSTANCE_ROOT, 'docstore')",
        "Folder for the docstore filesystem"
    ),
    ConfigOption(
        'REFDOC_ROOT',
        "os.path.join(INSTANCE_ROOT, 'refdocs')",
        "Folder for the refdocs filesystem"
    ),
    ConfigOption(
        'SHAREDCACHE_ROOT',
        "os.path.join(INSTANCE_ROOT, 'cache', 'shared')",
        "Folder for the shared cache filesystem"
    ),
    ConfigOption(
        'SVN_SERVER_ROOT',
        'None',
        'Path to the SVN root on the SVN server'
    ),
]

load_config(config_options_fs)


config_constants_fs = [
    ConfigConstant(
        'DOCUMENT_WALLET_PREFIX',
        "'wallet'",
        "Prefix for the Document Wallet in the expose hierarchy"
    ),
    ConfigConstant(
        'DOCSTORE_PREFIX',
        "'docstore'",
        "Prefix for the Docstore in the expose hierarchy"
    ),
    ConfigConstant(
        'REFDOC_PREFIX',
        "'refdocs'",
        "Prefix for refdocs in the expose hierarchy"
    ),
    ConfigConstant(
        'SHAREDCACHE_PREFIX',
        "'sharedcache'",
        "Prefix for sharedcache in the expose hierarchy"
    )
]

load_constants(config_constants_fs)

config_options_resources = [
    ConfigOption(
        "PRINTER_NAME",
        "{}",
        "Name of the printer to use for printing. "
        "Tendril will use 'lp -d PRINTER_NAME to print."
    ),
    ConfigOption(
        'USE_PREFAB_SERVER',
        'False',
        'Use Prefab Server'
    ),
    ConfigOption(
        'PREFAB_SERVER',
        'None',
        'Pre-assembled Datasets Server URL'
    ),
    ConfigOption(
        'MQ_SERVER',
        'None',
        'Message Queue Server Host'
    ),
    ConfigOption(
        'MQ_SERVER_PORT',
        '5672',
        'Message Queue Server Host'
    ),
    ConfigOption(
        'FIREFOX_PROFILE_PATH',
        "None",
        "Path to the firefox profile to use for splinter."
    )
]

load_config(config_options_resources)

config_options_services = [
    ConfigOption(
        "APPENLIGHT_PRIVATE_API_KEY",
        "{}",
        "Private API key to use with appenlight, if any."
    ),
    ConfigOption(
        "APPENLIGHT_PUBLIC_API_KEY",
        "{}",
        "Public API key to use with appenlight, if any."
    ),
    ConfigOption(
        "ENABLE_APPENLIGHT",
        "False",
        "Whether to use AppEnlight to monitor application."
    ),
    ConfigOption(
        "PIWIK_SITE_ID",
        "{}",
        "Site ID to use with Piwik."
    ),
    ConfigOption(
        "PIWIK_BASE_URL",
        "{}",
        "Base URL of the Piwik instance to use."
    ),
    ConfigOption(
        "ENABLE_PIWIK",
        "False",
        "Whether to use Piwik for analytics."
    ),
]

load_config(config_options_services)


config_options_geda = [
    ConfigOption(
        'EDA_HARMONIZE_IDENTS',
        'True',
        'Whether to harmonize idents by default.'
    ),
]

load_config(config_options_geda)


config_options_frontend = [
    ConfigOption(
        'USE_X_SENDFILE',
        "True",
        "Whether to use X-SENDFILE to send files from the web frontend. "
        "Note that your web server must also support and be configured "
        "to do this."
    ),
]

load_config(config_options_frontend)


config_options_security = [
    ConfigOption(
        'ADMIN_USERNAME',
        "None",
        "The username for the first Admin user"
    ),
    ConfigOption(
        'ADMIN_FULLNAME',
        "None",
        "The full name for the first Admin user"
    ),
    ConfigOption(
        'ADMIN_EMAIL',
        "None",
        "The e-mail for the first Admin user"
    ),
    ConfigOption(
        # TODO This is essentially public. Fix that.
        'ADMIN_PASSWORD',
        "None",
        "The password for the first Admin user"
    ),
    ConfigOption(
        # TODO This is essentially public. Fix that.
        'SECRET_KEY',
        "None",
        "The secret key for the frontend authentication system"
    )
]

load_config(config_options_security)

config_options_inventory = [
    ConfigOption(
        'INVENTORY_LOCATIONS',
        "[]",
        "A list of names of inventory locations"
    ),
    ConfigOption(
        'ELECTRONICS_INVENTORY_DATA',
        "[]",
        "A list of dictionaries specifying the locations and formats of "
        "inventory data."
    ),
]

load_config(config_options_inventory)


config_options_vendors = [
    ConfigOption(
        'VENDOR_DEFAULT_MAXAGE',
        "-1",
        "The maximum age in seconds after which sourcing information is "
        "considered stale. Set to -1 for no checks. The continuous background "
        "update is pretty unwieldy at present."
    ),
    ConfigOption(
        'VENDOR_MAP_FOLDER',
        "os.path.join(INSTANCE_ROOT, 'sourcing', 'maps')",
        "The folder in which vendor maps should be dumped"
    ),
    ConfigOption(
        'VENDOR_MAP_AUDIT_FOLDER',
        "os.path.join(AUDIT_PATH, 'vendor-maps')",
        "The folder in which the vendor maps audits should be dumped"
    ),
    ConfigOption(
        'PRICELISTVENDORS_FOLDER',
        "os.path.join(INSTANCE_ROOT, 'sourcing', 'pricelists')",
        "The folder in which the price lists for pricelist vendors "
        "are located."
    ),
    ConfigOption(
        'CUSTOMSDEFAULTS_FOLDER',
        "os.path.join(INSTANCE_ROOT, 'sourcing', 'customs')",
        "The folder in which customs defaults are located."
    ),
    ConfigOption(
        'OCTOPART_API_KEY',
        "None",
        "The OctoPart API Key to use for vendors based on the OctoPart API."
    ),
    ConfigOption(
        'MOUSER_API_KEY',
        'None',
        'The Mouser API Key to use for Mouser Electronics.'
    ),
    ConfigOption(
        'ARROW_API_KEY',
        'None',
        'The Arrow API Key to use for Arrow Electronics.'
    ),
    ConfigOption(
        'ARROW_API_LOGIN',
        'None',
        'The username to use with the Arrow API'
    ),
    ConfigOption(
        'VENDORS_DATA',
        "[]",
        "A list of dictionaries containing vendor details, one for each"
        "configured vendor."
    ),
]

load_config(config_options_vendors)


config_options_execution = [
    ConfigOption(
        'SUPPORT_INTERPRETER_PERSISTENCE',
        "False",
        "Whether tendril should support interpreter persistence. This "
        "is generally in the form of maintaining in-memory caches, "
        "reloading sources from the filesystem, etc. This slows "
        "startup time, and therefore is only appropriate for server "
        "deployments."
    ),
    ConfigOption(
        'WARM_UP_CACHES',
        "False",
        "Whether tendril caches should be warmed up on startup. This "
        "significantly slows startup time, and therefore is only "
        "appropriate for server deployments."
    ),
    ConfigOption(
        'ENABLE_THREADED_CONNECTORS',
        "False",
        "Whether threaded connectors to external services should be used. "
        "These connectors only provide interfaces to allow response to "
        "asynchronous external events, and are only appropriate for server "
        "deployments. These threaded connectors are currently used only in "
        "cases where a synchronous service is not viable, so disabling this "
        "will disable all features dependent on it. On the the other hand, "
        "these threads may introduce some unresolved instability. "
    ),
]

load_config(config_options_execution)


def doc_render(group):
    """
    Converts a list of :class:`ConfigOption` or :class:`ConfigConstant`
    into a list compatible with :mod:`sphinxcontrib.documentedlist` for
    generating the configuration parameter documentation.
    """
    return [[x.name, x.default, x.doc] for x in group]


all_config_option_groups = [
    [doc_render(config_options_paths),
     "Options to configure paths for various local resources"],
    [doc_render(config_options_fs),
     "Options to configure the 'filesystems' containing instance resources"],
    [doc_render(config_options_resources),
     "Options to configure details of various instance resources"],
    [doc_render(config_options_services),
     "Options to configure third-party infrastructure services integration"],
    [doc_render(config_options_geda),
     "Options to configure the gEDA installation and related resources"],
    [doc_render(config_options_frontend),
     "Options to configure the frontend"],
    [doc_render(config_options_security),
     "Options to configure security features"],
    [doc_render(config_options_inventory),
     "Options to configure inventory details"],
    [doc_render(config_options_vendors),
     "Options to configure vendor details"],
    [doc_render(config_options_execution),
     "Options to configure tendril execution behavior"]
]


all_config_constant_groups = [
    [doc_render(config_constants_basic),
     "Basic config constants"],
    [doc_render(config_constants_redirected),
     "Configuration constants, following INSTANCE_ROOT redirection if needed"],
    [doc_render(config_constants_fs),
     "Filesystems related constants"]
]
