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

import os

import structlog
from google.cloud.storage import Client

logger = structlog.getLogger(__name__)


def download_from_gcs(
    bucket_name: str,
    object_prefix: str,
    destination_dir: str = "superlinked_app",
    project_id: str | None = None,
) -> list[str]:
    os.makedirs(destination_dir, exist_ok=True)

    if project_id:
        client = Client(project=project_id)
    else:
        client = Client()

    downloaded_files = []

    blobs = client.list_blobs(bucket_name, prefix=object_prefix)
    filtered_blobs = [blob for blob in blobs if blob.name == object_prefix or blob.name.startswith(object_prefix + "/")]

    for blob in filtered_blobs:
        if filename := os.path.basename(blob.name):
            destination_file_name = os.path.join(destination_dir, filename)
            os.makedirs(os.path.dirname(destination_file_name), exist_ok=True)
            blob.download_to_filename(destination_file_name)
            downloaded_files.append(destination_file_name)
            logger.info("file downloaded", blob_location=blob.name, file=filename, destination=destination_file_name)

    return downloaded_files
