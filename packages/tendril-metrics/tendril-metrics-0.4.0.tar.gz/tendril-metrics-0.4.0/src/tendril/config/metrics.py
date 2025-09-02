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
Metrics Configuration Options
=============================
"""


from tendril.utils.config import ConfigOption
from tendril.utils import log
logger = log.get_logger(__name__, log.DEFAULT)

depends = [
    'tendril.config.core',
    'tendril.config.influxdb',
    'tendril.config.influxdb_buckets',
]


config_elements_metrics = [
    ConfigOption(
        'METRICS_BUCKET',
        "INFLUXDB_METRICS_BUCKET",
        "Bucket to use to store metrics. Currently expects InfluxDB"
    ),
    ConfigOption(
        'METRICS_TOKEN',
        "INFLUXDB_METRICS_TOKEN",
        "Token or auth to use to store metrics. Currently expects InfluxDB Token"
    ),
    ConfigOption(
        'METRICS_PUBLISH',
        "False",
        "Whether to publish metrics. Note that this requires a "
        "functioning influxdb instance and may have non-trivial "
        "performance implications."
    ),
]


def load(manager):
    logger.debug("Loading {0}".format(__name__))
    manager.load_elements(config_elements_metrics,
                          doc="Tendril Metrics Configuration")
