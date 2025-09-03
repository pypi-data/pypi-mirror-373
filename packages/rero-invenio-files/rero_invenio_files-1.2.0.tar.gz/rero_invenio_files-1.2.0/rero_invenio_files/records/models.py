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

from invenio_db import db
from invenio_files_rest.models import Bucket
from invenio_records.models import RecordMetadataBase
from invenio_records_resources.records.models import FileRecordModelMixin
from sqlalchemy_utils.types import UUIDType


class RecordMetadata(db.Model, RecordMetadataBase):
    """Model for Record module metadata."""

    __tablename__ = "objects"
    bucket_id = db.Column(UUIDType, db.ForeignKey(Bucket.id))
    bucket = db.relationship(Bucket)


class FileRecordMetadata(db.Model, RecordMetadataBase, FileRecordModelMixin):
    """Model for Record files module."""

    __tablename__ = "objects_files"
    __record_model_cls__ = RecordMetadata
