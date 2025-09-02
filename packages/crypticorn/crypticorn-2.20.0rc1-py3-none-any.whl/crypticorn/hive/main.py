from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Coroutine, Optional, Union

from pydantic import StrictInt

from crypticorn.hive import (
    ApiClient,
    Configuration,
    DataApi,
    DataVersion,
    FeatureSize,
    ModelsApi,
    StatusApi,
)
from crypticorn.hive.utils import download_file

if TYPE_CHECKING:
    from aiohttp import ClientSession


class HiveClient:
    """
    A client for interacting with the Crypticorn Hive API.
    """

    config_class = Configuration

    def __init__(
        self,
        config: Configuration,
        http_client: Optional[ClientSession] = None,
        is_sync: bool = False,
    ):
        self.config = config
        self.base_client = ApiClient(configuration=self.config)
        if http_client is not None:
            self.base_client.rest_client.pool_manager = http_client
        # Pass sync context to REST client for proper session management
        self.base_client.rest_client.is_sync = is_sync
        # Instantiate all the endpoint clients
        self.models = ModelsApi(self.base_client, is_sync=is_sync)
        self.data = DataApiWrapper(self.base_client, is_sync=is_sync)
        self.status = StatusApi(self.base_client, is_sync=is_sync)


class DataApiWrapper(DataApi):
    """
    A wrapper for the DataApi class.
    """

    def download_data(  # type: ignore[override]
        self,
        model_id: StrictInt,
        folder: Path = Path("data"),
        version: Optional[DataVersion] = None,
        feature_size: Optional[FeatureSize] = None,
        **kwargs,
    ) -> Union[list[Path], Coroutine[Any, Any, list[Path]]]:
        """
        Download data for model training. All three files (y_train, x_test, x_train) are downloaded and saved under e.g. FOLDER/v1/coin_1/*.feather.
        The folder will be created if it doesn't exist.
        Works in both sync and async contexts.

        :param model_id: Model ID (required) (type: int)
        :param version: Data version. Default is the latest public version. (optional) (type: DataVersion)
        :param feature_size: The number of features in the data. Default is LARGE. (optional) (type: FeatureSize)
        :return: A list of paths to the downloaded files.
        """
        if self.is_sync:
            return self._download_data_wrapper_sync(
                model_id=model_id,
                folder=folder,
                version=version,
                feature_size=feature_size,
                **kwargs,
            )
        else:
            return self._download_data_wrapper_async(
                model_id=model_id,
                folder=folder,
                version=version,
                feature_size=feature_size,
                **kwargs,
            )

    def _download_data_wrapper_sync(
        self,
        model_id: StrictInt,
        folder: Path = Path("data"),
        version: Optional[DataVersion] = None,
        feature_size: Optional[FeatureSize] = None,
        **kwargs,
    ) -> list[Path]:
        """
        Download data for model training (sync version).
        """
        response = self._download_data_sync(
            model_id=model_id,
            version=version,
            feature_size=feature_size,
            **kwargs,
        )
        base_path = f"{folder}/v{response.version.value}/coin_{response.coin.value}/"
        os.makedirs(base_path, exist_ok=True)

        return [
            download_file(
                url=response.links.y_train,
                dest_path=Path(base_path + "y_train_" + response.target + ".feather"),
            ),
            download_file(
                url=response.links.x_test,
                dest_path=Path(
                    base_path + "x_test_" + response.feature_size + ".feather"
                ),
            ),
            download_file(
                url=response.links.x_train,
                dest_path=Path(
                    base_path + "x_train_" + response.feature_size + ".feather"
                ),
            ),
        ]

    async def _download_data_wrapper_async(
        self,
        model_id: StrictInt,
        folder: Path = Path("data"),
        version: Optional[DataVersion] = None,
        feature_size: Optional[FeatureSize] = None,
        **kwargs,
    ) -> list[Path]:
        """
        Download data for model training (async version).
        """
        response = await self._download_data_async(
            model_id=model_id,
            version=version,
            feature_size=feature_size,
            **kwargs,
        )
        base_path = f"{folder}/v{response.version.value}/coin_{response.coin.value}/"
        os.makedirs(base_path, exist_ok=True)

        return [
            download_file(
                url=response.links.y_train,
                dest_path=Path(base_path + "y_train_" + response.target + ".feather"),
            ),
            download_file(
                url=response.links.x_test,
                dest_path=Path(
                    base_path + "x_test_" + response.feature_size + ".feather"
                ),
            ),
            download_file(
                url=response.links.x_train,
                dest_path=Path(
                    base_path + "x_train_" + response.feature_size + ".feather"
                ),
            ),
        ]
