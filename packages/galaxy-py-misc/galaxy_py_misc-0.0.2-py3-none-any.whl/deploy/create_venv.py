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
from virtualenv import cli_run
from virtualenvapi.manage import VirtualEnvironment
from typing import Dict,        \
                   List

project_dependencies: Dict[str, List[str]] = {
                                              "galaxy-app": [
                                                             "galaxy-utils",
                                                             "galaxy-service",
                                                             "galaxy-data",
                                                             "galaxy-kernel",
                                                             "galaxy-net",
                                                             "galaxy-error",
                                                             "galaxy-cmd",
                                                             "galaxy-proc",
                                                             "galaxy-engine",
                                                             "galaxy-perfo",
                                                             "galaxy-report",
                                                             "galaxy-comm",
                                                             "galaxy-algo"
                                                            ],
                                              "galaxy-data": [
                                                              "galaxy-utils",
                                                              "galaxy-err:wor",
                                                              "galaxy-service",
                                                              "galaxy-perfo"
                                                             ],
                                              "galaxy-error": ["galaxy-utils"],
                                              "galaxy-kernel": [
                                                                "galaxy-utils",
                                                                "galaxy-error",
                                                                "galaxy-service",
                                                                "galaxy-perfo"
                                                               ],
                                              "galaxy-net": [
                                                             "galaxy-utils",
                                                             "galaxy-kernel",
                                                             "galaxy-error",
                                                             "galaxy-service",
                                                             "galaxy-data",
                                                             "galaxy-perfo"
                                                            ],
                                              "galaxy-service": [
                                                                 "galaxy-utils",
                                                                 "galaxy-error",
                                                                 "galaxy-perfo"
                                                                ],
                                              "galaxy-proc": [
                                                              "galaxy-utils",
                                                              "galaxy-service",
                                                              "galaxy-kernel",
                                                              "galaxy-error",
                                                              "galaxy-net",
                                                              "galaxy-cmd",
                                                              "galaxy-data",
                                                              "galaxy-perfo",
                                                              "galaxy-report"
                                                             ],
                                             "galaxy-comm": [
                                                             "galaxy-utils",
                                                             "galaxy-service",
                                                             "galaxy-error",
                                                             "galaxy-data",
                                                             "galaxy-kernel",
                                                             "galaxy-net",
                                                             "galaxy-perfo",
                                                             "galaxy-report"
                                                            ],
                                             "galaxy-cmd": [
                                                            "galaxy-utils",
                                                            "galaxy-service",
                                                            "galaxy-error",
                                                            "galaxy-data",
                                                            "galaxy-kernel",
                                                            "galaxy-net",
                                                            "galaxy-app",
                                                            "galaxy-perfo",
                                                            "galaxy-report",
                                                            "galaxy-comm"
                                                           ],
                                             "galaxy-www": [
                                                            "galaxy-utils",
                                                            "galaxy-data",
                                                            "galaxy-error",
                                                            "galaxy-service",
                                                            "galaxy-perfo"
                                                           ],
                                             "galaxy-perfo": [
                                                              "galaxy-utils"
                                                             ],
                                             "galaxy-report": [
                                                               "galaxy-utils",
                                                               "galaxy-data",
                                                               "galaxy-error",
                                                               "galaxy-service",
                                                               "galaxy-perfo",
                                                               "galaxy-net"
                                                              ],
                                             "galaxy-engine": [
                                                               "galaxy-utils",
                                                               "galaxy-service",
                                                               "galaxy-error",
                                                               "galaxy-data",
                                                               "galaxy-perfo"
                                                              ],
                                             "galaxy-algo": [
                                                             "galaxy-utils",
                                                             "galaxy-service",
                                                             "galaxy-error",
                                                             "galaxy-data",
                                                             "galaxy-perfo"
                                                            ]
                                             }


def generate_pythonpath(proj: str) -> str:
    return "\n".join(["PYTHONPATH=\"{}:$PYTHONPATH\"".format(os.path.join(get_base_dir(), dep)) for dep in project_dependencies[proj]])


def generate_activate_pythonpath(proj: str) -> str:
    return """_OLD_VIRTUAL_PYTHONPATH="$PYTHONPATH"
{}
export PYTHONPATH

""".format(generate_pythonpath(proj))


def generate_deactivate_pythonpath() -> str:
    return """    if ! [ -z "${_OLD_VIRTUAL_PYTHONPATH+_}" ] ; then
        export PYTHONPATH="$_OLD_VIRTUAL_PYTHONPATH"
        unset _OLD_VIRTUAL_PYTHONPATH
    fi
"""


def modify_activate(proj: str, venv: str) -> None:
    if proj in project_dependencies:
        activate_file = os.path.join(venv, "bin", "activate")
        print("Modifying the activate file of the environment variable : {}".format(activate_file))
        lines = []
        with open(activate_file, "r") as fd:
            for line in fd:
                if line.strip().startswith("unset _OLD_VIRTUAL_PYTHONHOME"):
                    lines.append(line)
                    line = next(fd)
                    lines.append(line)
                    lines.append(generate_deactivate_pythonpath())
                elif line.strip().startswith("_OLD_VIRTUAL_PATH=\"$PATH\""):
                    lines.append(line)
                    line = next(fd)
                    lines.append(line)
                    line = next(fd)
                    lines.append(line)
                    line = next(fd)
                    lines.append(line)
                    lines.append(generate_activate_pythonpath(proj))
                else:
                    lines.append(line)
        with open(activate_file, "w+") as fd:
            for line in lines:
                fd.write(line)


def get_base_dir() -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(base_dir, "..", ".."))


def create_venv() -> None:
    for root, dirs, files in os.walk(get_base_dir()):
        for dr in [dr for dr in dirs if dr.startswith("galaxy-")]:
            venv_path = os.path.join(get_base_dir(), dr, "venv")
            req_path = os.path.join(get_base_dir(), dr, "requirements.txt")
            
            try:
                print("Creating the virtual environment : {}".format(venv_path))
                cli_run([venv_path])
                env = VirtualEnvironment(venv_path)
                print("Importing required packages into the virtual environment : {}".format(venv_path))
                try:
                    env.install("-r {}".format(req_path))
                except Exception as e:
                    print(e)
                modify_activate(dr, venv_path)
            except Exception as e:
                print(e)


if __name__ == "__main__":
    create_venv()
