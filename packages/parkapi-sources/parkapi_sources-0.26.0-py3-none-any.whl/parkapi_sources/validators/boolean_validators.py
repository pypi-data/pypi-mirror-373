"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Any

from validataclass.validators import BooleanValidator


class MappedBooleanValidator(BooleanValidator):
    mapping: dict[str, bool]

    def __init__(self, *args, mapping: dict[str, bool], **kwargs):
        super().__init__(*args, **kwargs)
        self.mapping = mapping

    def validate(self, input_data: Any, **kwargs) -> bool:
        if isinstance(input_data, str):
            input_data = input_data.lower()

        input_data = self.mapping.get(input_data, input_data)

        return super().validate(input_data, **kwargs)
