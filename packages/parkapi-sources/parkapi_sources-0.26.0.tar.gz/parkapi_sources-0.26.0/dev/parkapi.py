"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""


# ruff: noqa: T201

import sys
from pathlib import Path

sys.path.append(str(Path(Path(__file__).parent.parent, 'src')))  # noqa: E402

from parkapi_sources.scripts.parkapi import main

if __name__ == '__main__':
    main()
