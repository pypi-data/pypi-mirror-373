#  Copyright (c) 2022 bastien.saltel
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os
import shutil


def get_base_dir() -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(base_dir, "..", ".."))


def delete_venv() -> None:
    for root, dirs, files in os.walk(get_base_dir()):
        for dr in [dr for dr in dirs if dr.startswith("galaxy-")]:
            venv_path = os.path.join(get_base_dir(), dr, "venv")
            try:
                shutil.rmtree(venv_path)
            except Exception as e:
                print(venv_path)
                print(e)


if __name__ == "__main__":
    delete_venv()
