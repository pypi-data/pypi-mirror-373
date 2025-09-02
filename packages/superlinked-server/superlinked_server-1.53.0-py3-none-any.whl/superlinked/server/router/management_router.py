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

import sys
from datetime import datetime

import inject
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi_restful.cbv import cbv
from starlette import status

from superlinked.framework.common.util.version_resolver import VersionResolver
from superlinked.server.exception.exception import DataLoaderNotFoundException
from superlinked.server.middleware.api_key_auth import verify_api_key
from superlinked.server.service.data_loader import DataLoader

router = APIRouter()


@cbv(router)
class ManagementRouter:
    __data_loader: DataLoader = Depends(lambda: inject.instance(DataLoader))

    @router.get(
        "/health",
        summary="Returns with 200 OK, if the application is healthy",
        status_code=status.HTTP_200_OK,
    )
    async def health_check(self) -> JSONResponse:
        return JSONResponse(content={"message": "OK"}, status_code=status.HTTP_200_OK)

    @router.get(
        "/version",
        summary="Returns the current version of the application and the Superlinked framework",
        status_code=status.HTTP_200_OK,
    )
    async def version(self) -> JSONResponse:
        version_info = {
            "superlinked-server": VersionResolver.get_version_for_package("superlinked-server") or "unknown",
            "superlinked": VersionResolver.get_version_for_package("superlinked") or "unknown",
            "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "timestamp": str(datetime.now().astimezone().isoformat()),
        }

        return JSONResponse(content=version_info, status_code=status.HTTP_200_OK)

    @router.post(
        "/data-loader/{name}/run",
        summary=(
            "Returns with 202 ACCEPTED if the data loader found and started in the background. "
            "If the data loader is not found by the given name, 404 NOT FOUND."
        ),
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(verify_api_key)],
    )
    async def load_data(self, name: str) -> JSONResponse:
        try:
            await self.__data_loader.load(name)  # pylint: disable=no-member
            return JSONResponse(
                content={"result": f"Background task successfully started with name: {name}"},
                status_code=status.HTTP_202_ACCEPTED,
            )
        except DataLoaderNotFoundException:
            return JSONResponse(
                content={"result": f"Data load initiation failed, no source found with name: {name}"},
                status_code=status.HTTP_404_NOT_FOUND,
            )

    @router.get(
        "/data-loader/",
        summary="Returns 200 OK with the name and config of your data loaders",
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(verify_api_key)],
    )
    async def get_data_loaders(self) -> JSONResponse:
        loaders = self.__data_loader.get_data_loaders()  # pylint: disable=no-member
        return JSONResponse(
            content={"result": {name: str(config) for name, config in loaders.items()}},
            status_code=status.HTTP_200_OK,
        )
