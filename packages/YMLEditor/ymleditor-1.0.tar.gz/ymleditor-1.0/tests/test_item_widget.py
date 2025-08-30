from unittest.mock import MagicMock

from PyQt6.QtWidgets import QApplication, QComboBox, QLineEdit, QTextEdit
import pytest

from YMLEditor.item_widget import ItemWidget


@pytest.fixture(scope="module")
def app():
    """
    Create a QApplication instance for testing.
    Required for PyQt widgets.
    """
    return QApplication([])


@pytest.fixture
def mock_config():
    """
    Mock config object with `get`, `set`, `save`, and `load` methods.
    """
    config = MagicMock()
    config.get.side_effect = lambda key: {"key1": "value1", "key2": "value2"}.get(key, None)
    return config


@pytest.fixture
def mock_callback():
    """
    Mock callback function.
    """
    return MagicMock()


def test_item_widget_combo(app, mock_config, mock_callback):
    widget = ItemWidget(
        config=mock_config, widget_type="combo", initial_value="Option1",
        combo_rgx=["Option1", "Option2"], callback=mock_callback, key="key1", )
    assert isinstance(widget.widget, QComboBox)
    assert widget.widget.currentText() == "Option1"

def test_item_widget_line_edit(app, mock_config, mock_callback):
    widget = ItemWidget(
        config=mock_config, widget_type="line_edit", initial_value="Initial Text", combo_rgx=r"^\w+$",
        # Regex for validation
        callback=mock_callback, key="key2", )
    assert isinstance(widget.widget, QLineEdit)
    assert widget.widget.text() == "Initial Text"
    assert widget._rgx == r"^\w+$"


def test_item_widget_text_edit(app, mock_config, mock_callback):
    widget = ItemWidget(
        config=mock_config, widget_type="text_edit", initial_value="Multiline Text", combo_rgx=r".*",
        # Allow any text
        callback=mock_callback, text_edit_height=100, key="key3", )
    assert isinstance(widget.widget, QTextEdit)
    assert widget.widget.toPlainText() == "Multiline Text"
    assert widget.widget.height() == 100


def test_item_widget_read_only(app, mock_config, mock_callback):
    widget = ItemWidget(
        config=mock_config, widget_type="read_only", initial_value="Read-Only Text", combo_rgx=None,
        callback=mock_callback, key="key4", )
    assert isinstance(widget.widget, QLineEdit)
    assert widget.widget.text() == "Read-Only Text"
    assert widget.widget.isReadOnly()


def test_item_widget_on_widget_changed_invalid(app, mock_config, mock_callback):
    widget = ItemWidget(
        config=mock_config, widget_type="line_edit", initial_value="ValidText", combo_rgx=r"^\w+$",
        callback=mock_callback, key="key1", )
    line_edit = widget.widget
    line_edit.setText("Invalid Text!")  # Fails regex
    widget._on_widget_changed(line_edit)
    assert not widget._is_valid
    assert line_edit.styleSheet() == widget._error_style


def test_item_widget_set_text(app, mock_config, mock_callback):
    widget = ItemWidget(
        config=mock_config, widget_type="line_edit", initial_value="Initial", combo_rgx=None,
        callback=mock_callback, key="key1", )
    widget.set_text(widget.widget, "Updated Value")
    assert widget.widget.text() == "Updated Value"

def test_item_widget_set_none(app, mock_config, mock_callback):
    widget = ItemWidget(
        config=mock_config, widget_type="line_edit", initial_value="Initial", combo_rgx=None,
        callback=mock_callback, key="key1", )
    # 1) Set text
    widget.set_text(widget.widget, "Updated Value")
    assert widget.widget.text() == "Updated Value"
    # 2) Set None
    widget.set_text(widget.widget, None)
    assert widget.widget.text() == 'None'
    # 3) Set text
    widget.set_text(widget.widget, "Updated Value2")
    assert widget.widget.text() == "Updated Value2"


def test_item_widget_display(app, mock_config, mock_callback):
    widget = ItemWidget(
        config=mock_config, widget_type="line_edit", initial_value="", combo_rgx=None,
        callback=mock_callback, key="key1", )
    widget.display()
    assert widget.widget.text() == "value1"  # From mock_config.get()
