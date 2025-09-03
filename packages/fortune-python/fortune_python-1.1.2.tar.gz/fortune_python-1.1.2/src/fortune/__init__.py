# Copyright 2025 fortune-python contributors
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
import random
import re
from pathlib import Path
from typing import Final


DEFAULT_PATH = Path("/usr/share/games/fortune")
FORTUNE_PATH = os.getenv("FORTUNEPATH")

if FORTUNE_PATH is not None:
    DATFILES: Final[Path] = Path(FORTUNE_PATH)
elif DEFAULT_PATH.is_dir():
    DATFILES: Final[Path] = DEFAULT_PATH
else:
    DATFILES: Final[Path] = (Path(__file__) / '..' / 'datfiles').resolve()


def _get_files():
    files = os.listdir(DATFILES)
    files.remove('LICENSE')
    return [DATFILES / file for file in files]


def fortune():
    paths = _get_files()
    fortunes = []
    for path in paths:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            text = re.split(r'\r?\n%\r?\n', f.read())
        text = [fortune for fortune in text if fortune.strip('\n\r')]
        fortunes += text
    return random.choice(fortunes)
