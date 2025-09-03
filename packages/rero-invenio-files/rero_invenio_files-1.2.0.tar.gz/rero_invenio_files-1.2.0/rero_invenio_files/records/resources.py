# RERO-Invenio-Files
# Copyright (C) 2024 RERO.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Files support for the RERO invenio instances."""

from invenio_records_resources.resources import FileResource as BaseFileResource
from invenio_records_resources.resources import (
    FileResourceConfig as BaseFileResourceConfig,
)
from invenio_records_resources.resources import RecordResource as BaseRecordResource
from invenio_records_resources.resources import (
    RecordResourceConfig as BaseRecordResourceConfig,
)


class RecordResourceConfig(BaseRecordResourceConfig):
    """Record resource configuration."""

    url_prefix = "/records"
    blueprint_name = "records"


class RecordResource(BaseRecordResource):
    """Record resource"."""


class FileResourceConfig(BaseFileResourceConfig):
    """Record file resource configuration."""

    url_prefix = "/records/<pid_value>"
    blueprint_name = "records_files"


class FileResource(BaseFileResource):
    """Record file resource."""
