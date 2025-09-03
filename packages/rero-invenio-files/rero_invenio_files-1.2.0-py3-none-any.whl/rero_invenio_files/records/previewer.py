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

"""Files previewer."""

from flask import abort, current_app, request
from invenio_previewer import current_previewer
from invenio_previewer.api import PreviewFile as PreviewFileBase
from invenio_previewer.extensions import default
from invenio_records.errors import MissingModelError


class PreviewFile(PreviewFileBase):
    """Preview file default implementation."""

    @property
    def size(self):
        """Get file size."""
        return self.file.file.size

    @property
    def uri(self):
        """Get file download link.

        ..  note::

            The URI generation assumes that you can download the file using the
            view ``invenio_records_ui.<pid_type>_files``.
        """
        return f"/api/records/{self.pid.pid_value}/files/{self.file.key}/content"


def preview(pid, record, template=None, **kwargs):
    """Preview file for given record.

    Plug this method into your ``RECORDS_UI_ENDPOINTS`` configuration:

    .. code-block:: python

        RECORDS_UI_ENDPOINTS = dict(
            recid=dict(
                # ...
                route='/records/<pid_value/preview/<path:filename>',
                view_imp='invenio_previewer.views.preview',
                record_class='invenio_records_files.api:Record',
            )
        )
    """
    # Get file from record
    fileobj = current_previewer.record_file_factory(
        pid,
        record,
        request.view_args.get("filename", request.args.get("filename", type=str)),
    )
    if fileobj is None:
        abort(404)

    # Try to see if specific previewer is set
    file_previewer = fileobj.get("previewer")

    # Find a suitable previewer
    fileobj = PreviewFile(pid, record, fileobj)
    for plugin in current_previewer.iter_previewers(previewers=[file_previewer] if file_previewer else None):
        if plugin.can_preview(fileobj):
            try:
                return plugin.preview(fileobj)
            except Exception:
                current_app.logger.warning(
                    f"Preview failed for {fileobj.file.key}, in {fileobj.pid.pid_type}:{fileobj.pid.pid_value}",
                    exc_info=True,
                )
    return default.preview(fileobj)


def record_file_factory(pid, record, filename):
    """Get file from a record.

    :param pid: Not used. It keeps the function signature.
    :param record: Record which contains the files.
    :param filename: Name of the file to be returned.
    :returns: File object or ``None`` if not found.
    """
    try:
        if not (hasattr(record, "files") and record.files):
            return None
    except MissingModelError:
        return None

    try:
        return record.files[filename]
    except KeyError:
        return None
