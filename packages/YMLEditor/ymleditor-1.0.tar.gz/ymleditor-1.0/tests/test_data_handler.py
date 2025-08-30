import pytest

from YMLEditor.data_manager import DataHandler


class TestDataHandler:
    """Tests for the DataHandler class."""

    class ConcreteDataHandler(DataHandler):
        """Concrete implementation of DataHandler for testing."""

        def get(self, data, key):
            return super().get(data, key)

        def set(self, data, key, value):
            super().set(data, key, value)

        def items(self, data):
            return super().items(data)

    @pytest.fixture
    def handler(self):
        """Fixture to provide a ConcreteDataHandler instance."""
        return self.ConcreteDataHandler(verbose=0)

    def test_insert_valid(self, handler):
        data = [1, 2, 3]
        handler.insert(data, 1, 99)
        assert data == [1, 99, 2, 3]

    def test_insert_invalid_index(self, handler):
        data = [1, 2, 3]
        with pytest.raises(IndexError):
            handler.insert(data, 5, 99)

    def test_insert_non_list(self, handler):
        data = {"a": 1}
        with pytest.raises(ValueError):
            handler.insert(data, 0, 99)

    def test_delete_dict_key_exists(self, handler):
        data = {"a": 1, "b": 2}
        handler.delete(data, "a")
        assert data == {"b": 2}

    def test_delete_dict_key_missing(self, handler):
        data = {"a": 1}
        with pytest.raises(KeyError):
            handler.delete(data, "b")

    def test_delete_list_index_valid(self, handler):
        data = [1, 2, 3]
        handler.delete(data, 1)
        assert data == [1, 3]

    def test_delete_list_index_invalid(self, handler):
        data = [1, 2, 3]
        with pytest.raises(IndexError):
            handler.delete(data, 5)

    def test_delete_invalid_type(self, handler):
        data = 123
        with pytest.raises(TypeError):
            handler.delete(data, 1)

    def test_get_nested_key(self, handler):
        data = {"a": {"b": {"c": 42}}}
        assert handler.__getitem__(data, "a.b.c") == 42

    def test_get_missing_key(self, handler):
        data = {"a": {"b": {"c": 42}}}
        assert handler.__getitem__(data, "a.x.c") is None

    def test_set_nested_key(self, handler):
        data = {"a": {"b": {}}}
        handler.__setitem__(data, "a.b.c", 99)
        assert data == {"a": {"b": {"c": 99}}}

    def test_set_create_missing(self, handler):
        data = {"a": {}}
        handler.__setitem__(data, "a.b.c", 99)
        assert data == {"a": {"b": {"c": 99}}}

    def test_items_dict(self, handler):
        data = {"a": 1, "b": 2}
        items = list(handler.items(data))
        assert items == [("a", 1), ("b", 2)]

    def test_items_list(self, handler):
        data = [10, 20, 30]
        items = list(handler.items(data))
        assert items == [(0, 10), (1, 20), (2, 30)]

    def test_items_invalid_type(self, handler):
        data = 123
        with pytest.raises(TypeError):
            list(handler.items(data))

    def test_replace_indirect_valid(self, handler):
        data = {"INDIRECT": "_suffix", "KEY_suffix": 99}
        resolved_key = handler.replace_indirect(data, "KEY@INDIRECT")
        assert resolved_key == "KEY_suffix"

    def test_replace_indirect_invalid(self, handler):
        data = {"INDIRECT": "_suffix"}
        resolved_key = handler.replace_indirect(data, "KEY@MISSING")
        assert resolved_key is None

    def test_replace_indirect_no_at_symbol(self, handler):
        data = {"INDIRECT": "_suffix"}
        resolved_key = handler.replace_indirect(data, "KEY")
        assert resolved_key == "KEY"


class TestNavigateHierarchy:
    """Test suite for the _navigate_hierarchy method."""

    @pytest.fixture
    def mock_manager(self):
        """Mock DataManager with _navigate_hierarchy and _validate_index methods."""
        class MockDataManager:
            def _navigate_hierarchy(self, *args, **kwargs):
                return DataHandler._navigate_hierarchy(self, *args, **kwargs)
            def _validate_index(self, key):
                return DataHandler._validate_index(self, key)

        return MockDataManager()

    def test_navigate_dict_success(self, mock_manager):
        data = {"a": {"b": {"c": 1}}}
        target, key = mock_manager._navigate_hierarchy(data, "a.b.c", create_missing=False)
        assert target == {"c": 1}
        assert key == "c"

    def test_navigate_list_success(self, mock_manager):
        data = [{"x": 1}, {"y": 2}]
        target, key = mock_manager._navigate_hierarchy(data, "1.y", create_missing=False)
        assert target == {"y": 2}
        assert key == "y"

    def test_create_missing_dict(self, mock_manager):
        data = {"a": {"b": {}}}
        target, key = mock_manager._navigate_hierarchy(data, "a.b.c", create_missing=True)
        assert target == {}
        assert key == "c"

    def test_create_missing_list(self, mock_manager):
        data = []
        target, key = mock_manager._navigate_hierarchy(data, "2.x", create_missing=True)
        assert len(data) == 3  # List was extended
        assert target == {}
        assert key == "x"

    def test_index_out_of_range(self, mock_manager):
        data = [{"x": 1}]
        with pytest.raises(IndexError):
            mock_manager._navigate_hierarchy(data, "2.x", create_missing=False)

    def test_invalid_index(self, mock_manager):
        data = [{"x": 1}]
        with pytest.raises(ValueError):
            mock_manager._navigate_hierarchy(data, "a.x", create_missing=False)

    def test_type_error(self, mock_manager):
        data = 42  # Invalid type
        with pytest.raises(TypeError):
            mock_manager._navigate_hierarchy(data, "a.b.c", create_missing=True)

