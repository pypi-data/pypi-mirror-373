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

import hashlib
import os
from enum import Enum

from superlinked.server.configuration.settings import Settings


class HashType(Enum):
    MD5 = hashlib.md5


class FileHandlerService:
    def __init__(self, settings: Settings, hash_type: HashType | None = None) -> None:
        self.__hash_type = hash_type or HashType.MD5
        self.settings = settings

    def generate_filename(self, app_id: str) -> str:
        filename = self.__hash_type.value(f"{app_id}".encode()).hexdigest()
        return f"{self.settings.PERSISTENCE_FOLDER_PATH}/{filename}.json"

    def ensure_folder(self) -> None:
        os.makedirs(self.settings.PERSISTENCE_FOLDER_PATH, exist_ok=True)
