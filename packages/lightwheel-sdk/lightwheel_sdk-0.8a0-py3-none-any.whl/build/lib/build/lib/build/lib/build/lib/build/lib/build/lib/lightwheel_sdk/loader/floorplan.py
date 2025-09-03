# Copyright 2025 Lightwheel Team
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


from pathlib import Path
import zipfile
import threading
import shutil
import time
from concurrent.futures import Future, ThreadPoolExecutor
import requests
from tqdm import tqdm
from .exception import ApiException

CACHE_PATH = Path("~/.cache/lightwheel_sdk/floorplan/").expanduser()
CACHE_PATH.mkdir(parents=True, exist_ok=True)
from . import login_client


class FloorplanLoader:
    """
    Loader for floorplan USD files.

    Args:
        host (str): The host of the API
        max_workers (int, optional): The maximum number of workers for downloading USD files. Defaults to 4.
    """

    _latest_future: Future = None

    def __init__(self, host, max_workers=4):
        self.host = host
        self.headers = login_client.get_headers()
        self.lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._should_stop_downloading = False
        self.usd_suffix = ".usd"

    def acquire_usd(self, layout_id: int = None, style_id: int = None, *, scene: str = "robocasakitchen", backend="robocasa", cancel_previous_download: bool = True):
        try:
            self.check_version()
            if cancel_previous_download and self._latest_future and self._latest_future.running():
                self._should_stop_downloading = True
                # self._latest_future.cancel()
                while self._latest_future.running():
                    time.sleep(0.1)
                    print(f"waiting for cancel")
            self._latest_future = self.executor.submit(self.get_usd, scene, layout_id, style_id, backend)
        except Exception as e:
            print(e)
            if e.authenticated_failed():
                # login and retry
                self.headers = login_client.login(force_login=True)
                return self.acquire_usd(layout_id, style_id, scene=scene, backend=backend, cancel_previous_download=cancel_previous_download)
        return self._latest_future

    def check_version(self):
        version = self._get_version()
        if self._usd_cache_version_path().exists():
            with open(self._usd_cache_version_path(), "r") as f:
                cached_version = f.read()
            if cached_version == version:
                return
            self._clear_usd_cache()
            self._update_usd_cache_version(version)
        else:
            self._clear_usd_cache()
            self._update_usd_cache_version(version)

    def get_usd(self, scene: str, layout_id: int = None, style_id: int = None, backend: str = "robocasa"):
        from . import login_client

        try:
            return self._get_usd(scene, layout_id, style_id)
        except ApiException as e:
            if e.authenticated_failed():
                self.headers = login_client.login(force_login=True)
                return self._get_usd(scene, layout_id, style_id, backend)
            print(e)
        finally:
            pass

    def get_usd_by_id(self, id: str):
        response = requests.post(f"{self.host}/floorplan/v1/usd/id-get", json={"uuid": id}, timeout=60, headers=self.headers)
        if response.status_code != 200:
            raise ApiException(response)
        return response.json()

    def _get_usd(self, scene: str, layout_id: int = None, style_id: int = None, backend: str = "robocasa"):
        """
        Make a Get HTTP call to retrieve a bundle stream.

        Args:
            scene (str): The scene identifier
            layout_id (int): The layout ID
            style_id (int): The style ID

        Returns:
            str: The path to the downloaded USD file
        """
        try:
            data = {
                "scene": scene,
                "backend": backend,
            }
            if layout_id is not None:
                data["layout_id"] = layout_id
            if style_id is not None:
                data["style_id"] = style_id
            response = requests.post(f"{self.host}/floorplan/v1/usd/get", json=data, timeout=600, headers=self.headers)
            if response.status_code != 200:
                raise ApiException(response)
            res_json = response.json()
            s3_url = res_json["fileUrl"]
            metadata = res_json["metadata"]
            layout_id = metadata["layout_id"]
            style_id = metadata["style_id"]
            total_size = 0
            response = requests.get(s3_url, stream=True, timeout=600)
            if response.status_code != 200:
                raise ApiException(response)
            cache_dir_path = self._usd_cache_dir_path(dict(layout_id=layout_id, style_id=style_id))
            package_file_path = cache_dir_path.with_suffix(".zip")
            usd_file_path = cache_dir_path / f"scene{self.usd_suffix}"
            if usd_file_path.exists():
                return usd_file_path, metadata
            with open(package_file_path, "wb") as f:
                for chunk in tqdm(response.iter_content(chunk_size=1024), desc="Downloading Floorplan Package"):
                    if self._should_stop_downloading:
                        response.close()
                        print(f"stop downloading {layout_id}-{style_id}")
                        break
                    f.write(chunk)
                    total_size += len(chunk)
                print(f"dowloaded {total_size/1024/1024:.2f}MB")
        except Exception as e:
            raise e
        # decompress the package.zip to the cache_dir_path
        if not self._should_stop_downloading:
            with zipfile.ZipFile(package_file_path, "r") as zip_ref:
                zip_ref.extractall(CACHE_PATH)
        package_file_path.unlink()
        self._should_stop_downloading = False
        return usd_file_path, metadata

    def _usd_cache_dir_path(self, cache_key_args: dict):
        return CACHE_PATH / f"robocasakitchen-{cache_key_args['layout_id']}-{cache_key_args['style_id']}"

    def _clear_usd_cache(self):
        print(f"clear USD cache at {CACHE_PATH}")
        if not CACHE_PATH.exists():
            return
        for path in CACHE_PATH.glob("*"):
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()

    def _usd_cache_version_path(self):
        return CACHE_PATH / "version.txt"

    def _update_usd_cache_version(self, version: str):
        print(f"update USD cache version at {self._usd_cache_version_path()}")
        if not CACHE_PATH.exists():
            CACHE_PATH.mkdir(parents=True, exist_ok=True)
        with open(self._usd_cache_version_path(), "w") as f:
            f.write(version)

    def _get_version(self):
        """
        Make a GetVersion HTTP call to retrieve the version of the floorplan.

        Returns:
            str: The version of the floorplan
        """
        response = requests.post(f"{self.host}/floorplan/v1/version/get", json={}, timeout=60, headers=self.headers)
        if response.status_code != 200:
            raise ApiException(response)
        return response.json()["version"]
