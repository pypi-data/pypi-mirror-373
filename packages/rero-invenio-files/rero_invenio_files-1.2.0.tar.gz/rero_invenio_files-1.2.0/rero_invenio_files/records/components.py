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

"""Thumbnail generation and full text extraction component."""

import contextlib
import os
from io import BytesIO

import fitz
from invenio_records_resources.services.errors import FileKeyNotFoundError
from invenio_records_resources.services.files.components.base import (
    FileServiceComponent,
)
from wand.color import Color
from wand.image import Image


class ThumbnailAndFulltextComponent(FileServiceComponent):
    """Basic image metadata extractor."""

    @staticmethod
    def change_filename_extension(filename, extension):
        """Return filename with the given extension.

        Additionally, the original extension is appended to the filename, to avoid
        conflict with other files having the same name (without extension).
        """
        basename, ext = os.path.splitext(filename)

        if not basename:
            raise Exception(f"{filename} is not a valid filename")

        if not ext:
            return f"{basename}.{extension}"
        # remove dot
        ext = ext.replace(".", "")
        return f"{basename}-{ext}.{extension}"

    @staticmethod
    def create_thumbnail_from_file(file_path, mimetype):
        """Create a thumbnail from given file path and return image blob.

        :param file_path: Full path of file.
        :param mimetype: Mime type of the file.
        :returns: the binary data.
        """
        # Thumbnail can only be done from images or PDFs.
        if not mimetype.startswith("image/") and mimetype != "application/pdf":
            return None

        # For PDF, we take only the first page
        if mimetype == "application/pdf":
            # Append [0] force to take only the first page
            # file_path = file_path + "[0]"
            max_width = max_height = 200
            with fitz.open(file_path) as pdf_document:
                page = pdf_document[0]
                scale_factor = min(max_width / page.rect.width, max_height / page.rect.height)
                pixmap = page.get_pixmap(matrix=fitz.Matrix(scale_factor, scale_factor))
                return pixmap.tobytes(output="jpg", jpg_quality=95)

        else:
            # Create the image thumbnail
            with Image(filename=file_path) as img:
                img.format = "jpg"
                img.background_color = Color("white")
                img.alpha_channel = "remove"
                img.transform(resize="200x")

                return img.make_blob()

    @staticmethod
    def create_fulltext_from_file(file_path, mimetype):
        """Extract the fulltext for a given pdf file.

        :param file_path: str - the path of the file.
        :param mimetype: str - the mime type of the file.
        :returns: the extracted text.
        :rtype: str
        """
        if mimetype != "application/pdf":
            return None
        with fitz.open(file_path) as pdf_file:
            text = [page.get_text("text") for page in pdf_file]
            return "\n".join(text)

    def commit_file(self, identity, id_, file_key, record):
        """Commit file handler.

        :param identity: flask principal Identity
        :param id_: str - record file id.
        :param file_key: str - file key in the file record.
        :param record: obj - record instance.
        """
        # already a thumbnail
        if record.files[file_key].get("metadata", {}).get("type") == "thumbnail":
            return
        rfile = record.files[file_key].file
        sf = self.service
        recid = record.pid.pid_value
        # thumbnail
        with contextlib.suppress(Exception):
            if blob := self.create_thumbnail_from_file(rfile.uri, rfile.mimetype):
                thumb_name = self.change_filename_extension(file_key, "jpg")
                sf.init_files(
                    identity=identity,
                    id_=recid,
                    data=[
                        {
                            "key": thumb_name,
                            "metadata": {
                                "type": "thumbnail",
                                "thumbnail_for": file_key,
                            },
                        }
                    ],
                    uow=self.uow,
                )
                sf.set_file_content(
                    identity,
                    id_=recid,
                    file_key=thumb_name,
                    stream=BytesIO(blob),
                    uow=self.uow,
                )
                sf.commit_file(identity=identity, id_=recid, file_key=thumb_name, uow=self.uow)
        # fulltext
        with contextlib.suppress(Exception):
            if fulltext := self.create_fulltext_from_file(rfile.uri, rfile.mimetype):
                thumb_name = self.change_filename_extension(file_key, "txt")
                sf.init_files(
                    identity=identity,
                    id_=recid,
                    data=[
                        {
                            "key": thumb_name,
                            "metadata": {
                                "type": "fulltext",
                                "fulltext_for": file_key,
                            },
                        }
                    ],
                    uow=self.uow,
                )
                sf.set_file_content(
                    identity=identity,
                    id_=recid,
                    file_key=thumb_name,
                    stream=BytesIO(fulltext.encode()),
                    uow=self.uow,
                )
                sf.commit_file(identity=identity, id_=recid, file_key=thumb_name, uow=self.uow)

    def delete_file(self, identity, id_, file_key, record, deleted_file):
        """Delete file handler.

        :param identity: flask principal Identity
        :param id_: str - record file id.
        :param file_key: str - file key in the file record.
        :param record: obj - record instance.
        :param deleted_file: file instance - the deleted file instance.
        """
        # a thumbnail or a fulltext
        if deleted_file.get("metadata", {}).get("type") in ["thumbnail", "fulltext"]:
            return
        sf = self.service
        recid = record.pid.pid_value
        thumb_name = self.change_filename_extension(file_key, "jpg")
        with contextlib.suppress(FileKeyNotFoundError):
            sf.delete_file(identity=identity, id_=recid, file_key=thumb_name, uow=self.uow)
        fulltext_name = self.change_filename_extension(file_key, "txt")
        with contextlib.suppress(FileKeyNotFoundError):
            sf.delete_file(identity=identity, id_=recid, file_key=fulltext_name, uow=self.uow)
