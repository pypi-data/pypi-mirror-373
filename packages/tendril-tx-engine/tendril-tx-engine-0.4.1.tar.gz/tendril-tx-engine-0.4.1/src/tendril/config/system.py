# Copyright (C) 2025 Chintalagiri Shashank
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
System Configuration Options
=============================
"""

# TODO Move to core utils?

from tendril.utils.config import ConfigOption
from tendril.utils import log
logger = log.get_logger(__name__, log.DEFAULT)

depends = [
    'tendril.config.core'
]


config_elements_system = [
    ConfigOption(
        'SYS_PING',
        "'False'",
        "Whether to publish ping to the system. If true, ping will be sent to the "
        "MQ service 'amqp091:system' with the routing code 'ping.[COMPONENT_NAME]'."
    ),
]


def load(manager):
    logger.debug("Loading {0}".format(__name__))
    manager.load_elements(config_elements_system,
                          doc="Tendril Distributed System Configuration")
