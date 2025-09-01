"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Any


class ConfigHelper:
    _config: dict

    def __init__(self, config: dict):
        self._config = config

    def get(self, key: str, default: Any = None):
        return self._config.get(key, default)
