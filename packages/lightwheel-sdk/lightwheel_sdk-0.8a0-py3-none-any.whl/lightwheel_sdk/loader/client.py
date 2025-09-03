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

import os
import json
from typing import Dict, Any
import requests
import getpass
from pathlib import Path
from termcolor import colored
from .exception import ApiException

CACHE_PATH = Path("~/.cache/lightwheel_sdk/login/").expanduser()
CACHE_PATH.mkdir(parents=True, exist_ok=True)

AUTH_KEY = "Authorization"
USERNAME_KEY = "UserName"


class LightwheelClient:
    """
    Lightwheel client

    Args:
        host (str): The host of the Lightwheel API.
            If not provided, the host will be read from the LW_API_ENDPOINT environment variable.
            If the LW_API_ENDPOINT environment variable is not set, the default host will be https://api.lightwheel.net.
    """

    def __init__(
        self,
        *,
        host: str = "",
        base_timeout: int = 10,
    ):
        self.host = host
        self.base_timeout = base_timeout
        self.headers = {}
        if self.host == "":
            env_host = os.environ.get("LW_API_ENDPOINT", "https://api.lightwheel.net")
            self.host = env_host
        self.host = self.host.rstrip("/")

        x_envs = [k for k in os.environ.keys() if k.startswith("LW_SDK_HEADERS_")]
        print(x_envs)
        for x_env in x_envs:
            self.headers[x_env.replace("LW_SDK_HEADERS_", "").lower().replace("_", "-")] = os.environ[x_env]
            print(self.headers)
        self.cache_path = CACHE_PATH / "account.json"

    def get_headers(self):
        return self.headers

    def update_header(self, key: str, value: str):
        self.headers[key] = value

    def post(self, path: str, *, data: Dict[str, Any] = None, timeout: int = None):
        res = requests.post(
            f"{self.host}/{path.lstrip('/')}",
            headers=self.get_headers(),
            json=data,
            timeout=timeout or self.base_timeout,
        )
        if res.status_code == 401:
            self.login(force_login=True)
            return self.post(path, data=data, timeout=timeout)
        if res.status_code != 200:
            raise ApiException(res)
        return res

    def login(self, force_login=False):
        if not self.cache_path.exists() or force_login:
            account_data = {}
            account_data["username"] = input(colored("\nusername: ", "green"))
            account_data["password"] = getpass.getpass(colored("\npassword: ", "green"))
            response = self.post("/api/authenticate/v1/user/login", data={"username": account_data["username"], "password": account_data["password"]})
            if response.status_code != 200:
                if response.status_code == 500 and response.json().get("message", "").startswith("login failed"):
                    print(colored("Invalid username or password", "red"))
                    return self.login(force_login=True)
                raise ApiException(response)
            token = response.json()["token"]
            headers = {AUTH_KEY: f"Bearer {token}", USERNAME_KEY: account_data["username"]}
            account_data["headers"] = headers
            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump(account_data, f)
        else:
            with open(self.cache_path, "r", encoding="utf-8") as f:
                account_data = json.load(f)
            headers = account_data["headers"]
        self.update_header(AUTH_KEY, headers.get(AUTH_KEY, ""))
        self.update_header(USERNAME_KEY, headers.get(USERNAME_KEY, ""))
        return headers

    def get_login_headers(self):
        headers = {}
        if "LoaderUserName" in os.environ and "LoaderToken" in os.environ:
            headers = {AUTH_KEY: f"Bearer {os.environ['LoaderToken']}", USERNAME_KEY: os.environ["LoaderUserName"]}
        if self.cache_path.exists() and self.cache_path.is_file():
            with open(self.cache_path, "r", encoding="utf-8") as f:
                account_data = json.load(f)
            headers = account_data["headers"]
        self.update_header(AUTH_KEY, headers.get(AUTH_KEY, ""))
        self.update_header(USERNAME_KEY, headers.get(USERNAME_KEY, ""))
        return headers
