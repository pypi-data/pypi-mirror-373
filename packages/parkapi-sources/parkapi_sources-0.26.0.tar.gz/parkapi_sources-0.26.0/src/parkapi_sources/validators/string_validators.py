"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Any

from validataclass.validators import StringValidator


class NumberCastingStringValidator(StringValidator):
    def validate(self, input_data: Any, **kwargs) -> str:
        if isinstance(input_data, int) or isinstance(input_data, float):
            input_data = str(input_data)

        return super().validate(input_data, **kwargs)


class ReplacingStringValidator(StringValidator):
    mapping: dict[str, str]

    def __init__(self, *args, mapping: dict[str, str], **kwargs):
        super().__init__(*args, **kwargs)
        self.mapping = mapping

    def validate(self, input_data: Any, **kwargs) -> str:
        self._ensure_type(input_data, str)

        for search, replace in self.mapping.items():
            input_data = input_data.replace(search, replace)

        return super().validate(input_data, **kwargs)
