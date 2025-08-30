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

from functools import partial
from typing import Union, List

# Use PySide for imports and fall back to PyQt
try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QWidget, QLabel, QComboBox, QLineEdit, QSizePolicy, QTextEdit, QCheckBox, QSlider, \
        QDoubleSpinBox
except ImportError:
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import QWidget, QLabel, QComboBox, QLineEdit, QSizePolicy, QTextEdit, QCheckBox, QSlider, \
        QDoubleSpinBox


from YMLEditor.structured_text import to_text, data_type, parse_text, _ast_dictionary


class ItemWidget(QWidget):
    """
    A configurable widget for displaying and editing a single field from a config file.

    - Supports various widget types including editable text, combo boxes, etc.  See readme for details.
    - All user edits are validated and synchronized with the config data.

    **Methods**:
    """

    def __init__(
            self, config, widget_type, initial_value, combo_rgx, callback, width=50, key=None,
            text_edit_height=60, verbose=3, error_style="color: Orange;", style=None
    ):
        """
        Init

        Args:
            config(Config): Configuration handler to synchronize data.
            widget_type (str): Type of widget to create
                ("text_edit", "line_edit", "read_only", "combo", "label").
            initial_value (str): Initial value to populate the widget.
            combo_rgx (Union[List[str], str]): Dropdown options for combo boxes or
                regex for validating text fields or tuple with min/max for a slider
            callback (callable): Function to call when the widget value changes.
            width (int, optional): Fixed width for the widget. Defaults to 50.
            key (str, optional): Key for linking the widget to the config data.
            text_edit_height (int, optional): Height for text edit widgets. Defaults to 90.
            verbose (int, optional): Verbosity level. 0=silent, 3=warnings, 4=information.
                Defaults to 3.
            error_style (str, optional): style for indicating an error.
            style (str) : style for the widget
        """
        super().__init__()

        self._error_style = error_style
        self._rgx = None
        self._widget_type = widget_type
        self._callback = callback
        self._key = key
        self._config = config
        self._is_valid = False
        self._data_type = None
        self._verbose = verbose

        self._create_widget(widget_type, initial_value, combo_rgx, width, text_edit_height, style)

    def display(self):
        """
        Load and display our field from the config data.
        Prints a warning if our key is not found in config data.
        """
        key, val = None, None
        try:
            if self.widget:
                key = self.widget.objectName()
                if key:
                    val = self._config.get(key) or ""
                    if not self._data_type:
                        self._data_type = data_type(val)

                    self.set_text(self.widget, val)

        except Exception as e:
            key = key or "None"
            val = val or "None"
            self.warn(f"WARN:  key '{key}': {e} val '{val}'")

    def _on_widget_changed(self, widget, *args):
        """
        Handle changes to the widget's value: validate text. If valid,
        update the config data. Set style appropriately.

        Args:
            widget (QWidget): The widget whose value was changed.
        """
        key = widget.objectName()
        text = get_text(widget)

        # Ensure text is valid and properly formatted
        if isinstance(text, str) and self._data_type:
            text = text.strip()  # Remove surrounding whitespace
            try:
                if self._data_type == dict:
                    text = _ast_dictionary(text)
                elif self._data_type == list:
                    # Add enclosing brackets if not present and content is non-empty
                    if text and (not text.startswith("[") or not text.endswith("]")):
                        text = f"[{text}]"
            except Exception as e:
                self.warn(f"Widget get text error. Text is '{text}'")
                self.set_error_style(widget)
                return

        # Validate the text and parse it
        invalid, data_value = parse_text(text, self._data_type, self._rgx)

        # Update config and apply styles based on validation
        if invalid:
            self.warn(f"parse error for {text}")
            self.set_error_style(widget)
        else:
            try:
                self._config.set(key, data_value)
                self.set_normal_style(widget)
            except Exception as e:
                self.set_error_style(widget)
                self.info(f"Error setting {text}")
            self._callback(key, text)

    def set_error_style(self, widget, message=None):
        """
        Apply an error style to the widget.

        Args:
            widget (QWidget): The widget to style.
            message (str, optional): Optional error message to display.
        """
        if not widget.property("originalStyle"):
            name = widget.objectName()
            widget.setProperty("originalStyle", widget.styleSheet())

        widget.setStyleSheet(self._error_style)
        if message:
            widget.setText(message)

    def set_normal_style(self, widget):
        """
        Restore the widget's default style.

        Args:
            widget (QWidget): The widget to restore.
        """
        original_style = widget.property("originalStyle")
        widget.setStyleSheet(original_style)

    def _create_widget(self, widget_type, initial_value, options, width, text_edit_height, style):
        """
        Create a specific type of widget based on the provided parameters (private).

        Args:
            widget_type (str): The type of widget to create.
            initial_value (str): The initial value for the widget.
            options (Union[List, str], optional): Regex for text fields, widget options for others.
            width (int): Width of the widget.
            text_edit_height (int): Height for text edit widgets.
            style (str): Style for the widget.
        """
        # Validate options based on widget type
        if widget_type in ["combo", "slider", "spinbox"] and not isinstance(options, list):
            raise ValueError(f"Options for '{widget_type}' must be a list. Got: {type(options).__name__}")

        if widget_type == "slider":
            if len(options) != 2 or not all(isinstance(i, int) for i in options):
                raise ValueError(
                    f"Options for 'slider' must be a list of two integers [min, max]. Got: {options}"
                )

        if widget_type == "spinbox":
            if len(options) != 4 or not (
                isinstance(options[0], (int, float)) and
                isinstance(options[1], (int, float)) and
                isinstance(options[2], (int, float)) and
                isinstance(options[3], int)
            ):
                raise ValueError(
                    f"Options for 'spinbox' must be a list of [min (float), max (float), step (float), precision (int)]. "
                    f"Got: {options}"
                )

        if widget_type == "combo" and not all(isinstance(i, str) for i in options):
            raise ValueError(
                f"Options for 'combo' must be a list of strings. Got: {options}"
            )

        # Create Widget
        if widget_type == "combo":
            self.widget = QComboBox()
            self.widget.addItems(options)
            self.set_text(self.widget, initial_value)
            self.widget.currentIndexChanged.connect(partial(self._on_widget_changed, self.widget))
        elif widget_type == "text_edit":
            self.widget = QTextEdit(str(initial_value))
            self.widget.setFixedHeight(text_edit_height)
            self.widget.setAcceptDrops(False)
            self._rgx = options
            self.widget.textChanged.connect(partial(self._on_widget_changed, self.widget))
        elif widget_type == "line_edit":
            self.widget = QLineEdit(str(initial_value))
            self.widget.setAcceptDrops(False)
            self._rgx = options
            self.widget.textChanged.connect(partial(self._on_widget_changed, self.widget))
        elif widget_type == "read_only":
            self.widget = QLineEdit(str(initial_value))
            self.widget.setReadOnly(True)
        elif widget_type == "label":
            self.widget = QLabel()
        elif widget_type == "checkbox":
            self.widget = QCheckBox()
            self.set_text(self.widget, initial_value)
            self.widget.stateChanged.connect(partial(self._on_widget_changed, self.widget))
        elif widget_type == "slider":
            self.widget = QSlider(Qt.Orientation.Horizontal)
            self.widget.setMinimum(options[0])
            self.widget.setMaximum(options[1])
            self.set_text(self.widget, initial_value)
            self.widget.valueChanged.connect(partial(self._on_widget_changed, self.widget))
        elif widget_type == "spinbox":
            self.widget = QDoubleSpinBox()
            self.widget.setMinimum(options[0])
            self.widget.setMaximum(options[1])
            self.widget.setSingleStep(options[2])
            self.widget.setDecimals(options[3])
            self.set_text(self.widget, initial_value)
            self.widget.valueChanged.connect(partial(self._on_widget_changed, self.widget))
        else:
            raise TypeError(f"Unsupported widget type: {widget_type} for {self._key}")

        if widget_type not in ["label"]:
            self.widget.setObjectName(self._key)

        if style:
            self.widget.setStyleSheet(style)

        self.widget.setProperty("originalStyle", self.widget.styleSheet())
        if isinstance(self.widget, QLineEdit):
            self.widget.setFixedWidth(width)
        else:
            self.widget.setMinimumWidth(width)

        self.widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)


    def set_text(self, widget, data):
        """
        Update the widget's value with the provided value.

        Args:
            widget (QWidget): The widget to update.
            data (str, int, float, bool, or dict): The data to update in the widget.
        """
        self.widget.blockSignals(True)

        if isinstance(widget, QComboBox):
            widget.setCurrentText(str(data))
        elif isinstance(widget, QLineEdit):
            if self._widget_type == "read_only":
                # Remove quotes, braces, and square brackets from str(data)
                cleaned_data = str(data).strip("[]{}").replace("'", "").replace('"', "")
                widget.setText(cleaned_data)
            else:
                widget.setText(str(data))
        elif isinstance(widget, QTextEdit):
                widget.setPlainText(str(data))
        elif isinstance(widget, QCheckBox):
            widget.setChecked(data == '1' or data == 'True')
        elif isinstance(widget, QSlider):
            if data:
                widget.setValue(int(data))
        elif isinstance(widget, QDoubleSpinBox):
            if data:
                widget.setValue(float(data))
        else:
            self.widget.blockSignals(False)
            raise TypeError(f"Unsupported widget type for setting value: {type(widget)}")

        self.widget.blockSignals(False)

    def warn(self, text):
        if self._verbose > 2:
            print(f"Warning: {text}")

    def info(self, text):
        if self._verbose > 3:
            print(f"Info: {text}")

def get_text(widget):
    """
    Retrieve the value from a widget.

    Args:
        widget (QWidget): The widget to retrieve the value from.

    Returns:
        str: The current value of the widget as a string.
    """
    if isinstance(widget, QComboBox):
        return widget.currentText()
    elif isinstance(widget, QTextEdit):
        return widget.toPlainText()
    elif isinstance(widget, QCheckBox):
        return "1" if widget.isChecked() else "0"
    elif isinstance(widget, QSlider):
        return str(widget.value())
    elif isinstance(widget, QDoubleSpinBox):
        # Round to the precision set in the QDoubleSpinBox
        precision = widget.decimals()
        value = round(widget.value(), precision)
        return f"{value:.{precision}f}"  # Format to ensure consistent decimal places
    elif hasattr(widget, "text"):
        return widget.text()
    else:
        raise TypeError(f"Unsupported widget type: {type(widget)}")
