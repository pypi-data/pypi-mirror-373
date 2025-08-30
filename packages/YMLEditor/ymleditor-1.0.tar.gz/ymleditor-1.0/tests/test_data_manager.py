from unittest.mock import patch

import pytest

from YMLEditor.data_manager import DataManager


class TestDataManager:
    """Test suite for the DataManager abstract base class."""

    @pytest.fixture
    def data_manager(self):
        """Fixture to provide a subclass of DataManager for testing."""

        class TestDataManager(DataManager):
            def _load_data(self, f):
                # Mock load implementation
                return {"key": "value"}

            def _save_data(self, f, data):
                # Mock save implementation
                pass

        return TestDataManager(verbose=1)

    def test_set_get(self, data_manager):
        # 1. Initialize "key" to "value" and verify
        data_manager._data = {"key": "value"}
        assert data_manager.get("key") == "value", "Failed to set and retrieve 'key' as 'value'"

        # 2. Set "key2" to None and verify
        data_manager.set("key2", None)
        assert data_manager.get("key2") is None, "Failed to set and retrieve 'key2' as None"

        # 3. Set "key" to "value" again and verify
        data_manager.set("key2", "value")
        assert data_manager.get("key2") == "value", \
            "Failed to set and retrieve 'key2' as 'value' again"

    def test_initialization(self, data_manager):
        """Test the initialization of DataManager."""
        assert data_manager.verbose == 1
        assert data_manager._data is None
        assert data_manager.file_path is None
        assert data_manager.unsaved_changes is False
        assert data_manager.snapshots == []

    def test_save_success(self, data_manager, tmp_path):
        """Test saving data successfully."""
        file_path = tmp_path / "test_file.json"
        data_manager.file_path = str(file_path)
        data_manager._data = {"key": "value"}
        data_manager.unsaved_changes = True

        with patch.object(data_manager, '_save_data', return_value=None):
            assert data_manager.save()
            assert not data_manager.unsaved_changes

    def test_save_without_file_path(self, data_manager):
        """Test saving without a file path."""
        data_manager._data = {"key": "value"}
        with pytest.raises(ValueError):
            data_manager.save()

    def test_save_without_data(self, data_manager):
        """Test saving without data."""
        data_manager.file_path = "test_file.json"
        with pytest.raises(ValueError):
            data_manager.save()

    def test_snapshot_push(self, data_manager):
        """Test pushing snapshots."""
        data_manager.init_data({"key": "value1"})
        data_manager.snapshot_push()
        assert len(data_manager.snapshots) == 2

        # Test max snapshot limit
        for i in range(data_manager.max_snapshots):
            data_manager.snapshot_push()
        assert len(data_manager.snapshots) == data_manager.max_snapshots

    def test_snapshot_undo(self, data_manager):
        """Test undo functionality."""
        data_manager.init_data({"key": "value1"})
        data_manager.snapshot_push()
        data_manager.set("key", "value2")
        data_manager.snapshot_push()

        data_manager.snapshot_undo()
        assert data_manager._data == {"key": "value2"}

        data_manager.snapshot_undo()
        assert data_manager._data == {"key": "value1"}

    def test_get_and_set(self, data_manager):
        """Test get and set operations."""
        data_manager.init_data({"key": "value"})
        assert data_manager.get("key") == "value"

        data_manager.set("key", "new_value")
        assert data_manager.get("key") == "new_value"

    def test_add_proxy(self, data_manager):
        """Test adding a proxy file."""
        proxy_file = "proxy_file"
        keys = ["key1", "key2"]

        data_manager.register_proxy_file(proxy_file, keys)
        assert data_manager._get_proxy("key1") == proxy_file
        assert data_manager._get_proxy("key2") == proxy_file

        # Adding duplicate key should raise ValueError
        with pytest.raises(ValueError):
            data_manager.register_proxy_file(proxy_file, ["key1"])

    def test_delete(self, data_manager):
        """Test delete operation."""
        data_manager.init_data({"key1": "value1", "key2": "value2"})
        data_manager.delete("key1")
        assert "key1" not in data_manager._data

    def test_insert(self, data_manager):
        """Test insert operation."""
        data_manager.init_data([])
        data_manager.insert(0, "item1")
        assert data_manager.get(0) == "item1"
