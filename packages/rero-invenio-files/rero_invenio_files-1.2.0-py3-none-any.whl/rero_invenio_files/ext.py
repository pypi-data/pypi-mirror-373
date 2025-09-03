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

from invenio_base.utils import obj_or_import_string

from . import config
from .records.resources import FileResource, RecordResource
from .records.services import RecordFileService, RecordService


class REROInvenioFiles:
    """RERO-Invenio-Files extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.extensions["rero-invenio-files"] = self
        self.init_services(app)
        self.init_resources(app)

    def service_configs(self, app):
        """Return custom service configs."""

        class ServiceConfigs:
            records = obj_or_import_string(app.config["RERO_FILES_RECORD_SERVICE_CONFIG"])
            records_files = obj_or_import_string(app.config["RERO_FILES_RECORD_FILE_SERVICE_CONFIG"])

        return ServiceConfigs

    def resource_configs(self, app):
        """Return custom resource configs."""

        class ResourceConfigs:
            records = obj_or_import_string(app.config["RERO_FILES_RECORD_RESOURCE_CONFIG"])
            records_files = obj_or_import_string(app.config["RERO_FILES_RECORD_FILE_RESOURCE_CONFIG"])

        return ResourceConfigs

    def init_services(self, app):
        """Initialize services."""
        service_configs = self.service_configs(app)
        self.records_service = RecordService(config=service_configs.records)
        self.records_files_service = RecordFileService(config=service_configs.records_files)

    def init_resources(self, app):
        """Initialize resources."""
        resource_configs = self.resource_configs(app)
        self.records_resource = RecordResource(
            service=self.records_service,
            config=resource_configs.records,
        )
        self.records_files_resource = FileResource(
            service=self.records_files_service, config=resource_configs.records_files
        )

    def init_config(self, app):
        """Initialize configuration."""
        for k in dir(config):
            if k.startswith("RERO_FILES_"):
                app.config.setdefault(k, getattr(config, k))


def finalize_app(app):
    """Finalize app."""
    # Invenio-Records-Resources
    init(app)


def api_finalize_app(app):
    """Finalize app for api."""
    init(app)


def init(app):
    """Init app."""
    # Register services - cannot be done in extension because
    # Invenio-Records-Resources might not have been initialized.
    sregistry = app.extensions["invenio-records-resources"].registry
    ext = app.extensions["rero-invenio-files"]
    sregistry.register(ext.records_service, service_id="records")
    sregistry.register(ext.records_files_service, service_id="records-files")
    # Register indexers
    iregistry = app.extensions["invenio-indexer"].registry
    iregistry.register(ext.records_service.indexer, indexer_id="records")
