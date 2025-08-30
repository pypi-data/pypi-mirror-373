#  Copyright (c) 2024.
#   Permission is hereby granted, free of charge, to any person obtaining a
#   copy of this software and associated documentation files (the “Software”), to deal in the
#   Software without restriction,
#   including without limitation the rights to use, copy, modify, merge, publish, distribute,
#   sublicense, and/or sell copies
#   of the Software, and to permit persons to whom the Software is furnished to do so, subject to
#   the following conditions:
#  #
#   The above copyright notice and this permission notice shall be included in all copies or
#   substantial portions of the Software.
#  #
#   THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
#   BUT NOT LIMITED TO THE
#   WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO
#   EVENT SHALL THE AUTHORS OR
#   COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
#   CONTRACT, TORT OR
#   OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#   DEALINGS IN THE SOFTWARE.
#  #
#   This uses QT for some components which has the primary open-source license is the GNU Lesser
#   General Public License v. 3 (“LGPL”).
#   With the LGPL license option, you can use the essential libraries and some add-on libraries
#   of Qt.
#   See https://www.qt.io/licensing/open-source-lgpl-obligations for QT details.

#
#
import os

import yaml
from YMLEditor.data_manager import DataManager


class YamlConfig(DataManager):
    """
    Handles loading and saving YAML files.

    Extends DataManager:
        - Implements YAML specific file _load_data, _save_data

    Inherits DataManager base file handling functionality:
        - load, save, get, set, and undo.

    **Methods**:
    """

    def _load_data(self, f):
        # This will load data from a YAML file
        data = yaml.safe_load(f)

        # Handle case where data is None (empty file) or incorrect format
        if data is None:
            if os.path.exists(self.file_path):
                # File is unreadable as YML
                print(f"Warning: {self.file_path} is not a valid YAML file.")
        return data

    def _save_data(self, f, data):
        # Save data in YAML format
        if data:
            # Save the updated data to the file
            yaml.safe_dump(data, f, sort_keys=False, default_flow_style=False)
        else:
            raise ValueError("_data is None")
