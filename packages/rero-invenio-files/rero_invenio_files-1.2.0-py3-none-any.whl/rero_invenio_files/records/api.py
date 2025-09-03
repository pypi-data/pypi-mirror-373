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

from invenio_pidstore.providers.recordid_v2 import RecordIdProviderV2
from invenio_records.systemfields import ConstantField, ModelField
from invenio_records_resources.records.api import FileRecord as FileRecordBase
from invenio_records_resources.records.api import Record as RecordBase
from invenio_records_resources.records.systemfields import (
    FilesField,
    IndexField,
    PIDField,
)

from . import models


class FileRecord(FileRecordBase):
    """Object record file API."""

    model_cls = models.FileRecordMetadata
    # defined later
    record_cls = None


class Record(RecordBase):
    """Record class to store file metadata."""

    # Configuration
    model_cls = models.RecordMetadata
    # System fields
    schema = ConstantField("$schema", "local://records/record-v1.0.0.json")
    # expires_at = ModelField()
    index = IndexField("records-record-v1.0.0", search_alias="records")
    # persistant identifier
    pid = PIDField("id", provider=RecordIdProviderV2)


class RecordWithFile(Record):
    """Record with files."""

    # files field
    files = FilesField(store=False, file_cls=FileRecord)
    # buckets
    bucket_id = ModelField()
    bucket = ModelField(dump=False)


# record class
FileRecord.record_cls = RecordWithFile
