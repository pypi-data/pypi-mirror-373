# Copyright 2024 Superlinked, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import inject

from superlinked.server.configuration.settings import settings
from superlinked.server.service.data_loader import DataLoader
from superlinked.server.service.file_handler_service import FileHandlerService
from superlinked.server.service.file_object_serializer import FileObjectSerializer
from superlinked.server.service.persistence_service import PersistenceService


def register_dependencies() -> None:
    inject.clear_and_configure(_configure)


def _configure(binder: inject.Binder) -> None:
    file_handler_service = FileHandlerService(settings)
    serializer = FileObjectSerializer(file_handler_service)
    binder.bind(DataLoader, DataLoader())
    binder.bind(PersistenceService, PersistenceService(serializer))
