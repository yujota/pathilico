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
import os
import typing
from logging import getLogger

import pathilico.pygletelm.effect as effect


if typing.TYPE_CHECKING:
    pass


# Helper functions
WSI_FILE_FORMATS = ("svs", "ndpi")


def explore_files(
        dir_paths: typing.Tuple[str, ...]
) -> typing.Tuple[typing.Tuple[str, ...], typing.Tuple[str, ...]]:
    paths, names = list(), list()
    dir_paths = [os.path.expanduser(p) for p in dir_paths]
    for d_path in dir_paths:
        for f_name in os.listdir(d_path):
            if f_name.split(".")[-1] in WSI_FILE_FORMATS:
                paths.append(os.path.join(d_path, f_name))
                names.append(f_name)
    return tuple(names), tuple(paths)


class ExploreFiles(effect.InstantCommandBase):

    def __init__(self, dir_paths, msg, msg_kwargs=None, logger=None):
        self.msg_constructor = msg
        self.msg_kwargs = msg_kwargs or dict()
        self.dir_paths = dir_paths
        self.logger = logger or getLogger("pfapp.FileExplore")
        super().__init__()

    def get_message(self):
        try:
            ns, ps = explore_files(self.dir_paths)
            msg = self.msg_constructor(
                file_names=ns, file_paths=ps,
                **self.msg_kwargs
            )
            return True, msg
        except Exception as e:
            self.logger.error(e)
            return False, e


def get_explore_file_commands(dir_paths, message, msg_kwargs=None):
    cmd = ExploreFiles(dir_paths, message, msg_kwargs=msg_kwargs)
    cmds = effect.EffectObject(instants=[cmd])
    return cmds


if __name__ == "__main__":
    ef = ExploreFiles(("~/DataForML/svs",), dict)
    flag, msg = ef.get_message()
    print(msg)
