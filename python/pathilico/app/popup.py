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
"""
Tkinter
"""
import os
import tkinter
import tkinter.filedialog


def ask_filename(root_dir=None, title="Select file"):
    root_dir = root_dir or os.path.expanduser("~")
    tk_window = tkinter.Tk()
    tk_window.geometry('0x0+0+0')
    file_name = tkinter.filedialog.askopenfilename(
        initialdir=root_dir, title=title,
        filetypes=(("Aperio file", "*.svs"), ("All files", "*.*"))
    )
    tk_window.withdraw()
    tk_window.destroy()
    if not isinstance(file_name, str):
        file_name = ""
    return file_name


if __name__ == "__main__":
    n = ask_filename()
    print(n)
