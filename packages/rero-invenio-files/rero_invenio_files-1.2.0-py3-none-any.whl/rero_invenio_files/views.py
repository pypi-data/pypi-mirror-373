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

"""Flask views."""

from flask import Blueprint

blueprint = Blueprint("rero_invenio_files", __name__)


def create_records_blueprint_from_app(app):
    """Create records blueprint for invenio-records-resources."""
    return app.extensions["rero-invenio-files"].records_resource.as_blueprint()


def create_records_files_blueprint_from_app(app):
    """Create records-files blueprint for invenio-records-resources."""
    return app.extensions["rero-invenio-files"].records_files_resource.as_blueprint()
