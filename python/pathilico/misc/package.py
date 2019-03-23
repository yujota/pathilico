#   Copyright
#     2019 Department of Dermatology, School of Medicine, Tohoku University
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
import sys
import os
import hashlib
import platform


def get_path(path, level=2, mod_name="pathilico"):
    """Return path in site-package when installed"""
    if mod_name in sys.modules:
        mod_path = getattr(sys.modules[mod_name], "__file__", "")
        if mod_path:
            parent_dir = get_parent_path(mod_path, level=1)
            result = os.path.join(parent_dir, path)
            if os.path.exists(result):
                return result

    parent = get_parent_path(path, level)
    result = os.path.join(parent, path)
    return result


def get_parent_path(path, level=2):
    if level == 0:
        return path
    elif level >= 1:
        return get_parent_path(os.path.dirname(path), level=level-1)


def get_md5hash(path):
    with open(path, "rb") as f:
        md5hash = hashlib.md5(f.read()).hexdigest()
    return md5hash


def recursive_listdir(paths, is_ok_file=lambda x: True):
    def rec(dir_path):
        for root, dirs, files in os.walk(dir_path):
            yield root
            for f in files:
                yield os.path.join(root, f)
    result = list()
    for path in paths:
        _ = [result.append(p) for p in rec(path)]
    return [p for p in result if is_ok_file(p)]


def get_exec_env_parameters():
    """Params of env such as os info, cpu arch, python ver, etc.

    :return Dict[str, str]:
    """
    result = dict()
    result["OperatingSystem"] = platform.system()
    result["MachineHostName"] = platform.node()
    result["OSReleaseInfo"] = platform.release()
    result["CPU"] = platform.machine()
    result["PythonVersion"] = platform.python_version()
    return result

