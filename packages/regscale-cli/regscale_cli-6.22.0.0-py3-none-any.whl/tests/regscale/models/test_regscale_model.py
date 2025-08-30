from typing import Optional
from unittest.mock import Mock, patch

import pytest

from regscale.models.regscale_models.regscale_model import RegScaleModel


class TestModel(RegScaleModel):
    _unique_fields = [["name"]]
    _parent_id_field = "parentId"
    id: Optional[int] = None
    name: str
    value: int
    parentId: int
    parentModule: str = "test_module"


class TestModelMultipleUnique(RegScaleModel):
    _unique_fields = [["field1", "field2"], ["field3"]]
    _parent_id_field = "parentId"
    id: Optional[int] = None
    field1: Optional[str] = None
    field2: Optional[str] = None
    field3: Optional[str] = None
    parentId: int
    parentModule: str = "test_module"


@pytest.fixture
def mock_api_handler():
    with patch("regscale.models.regscale_models.regscale_model.APIHandler") as mock:
        yield mock


@pytest.fixture
def mocked_model():
    with patch.object(TestModel, "get_cached_object") as mock_get_cached, patch.object(
        TestModel, "cache_object"
    ) as mock_cache, patch.object(TestModel, "create") as mock_create, patch.object(
        TestModel, "_perform_save"
    ) as mock_perform_save:
        yield TestModel(name="test", value=1, parentId=1), {
            "get_cached": mock_get_cached,
            "cache": mock_cache,
            "create": mock_create,
            "perform_save": mock_perform_save,
        }


def test_create_new_instance(mocked_model):
    model, mocks = mocked_model
    mocks["get_cached"].return_value = None
    mocks["create"].return_value = TestModel(id=1, name="test", value=1, parentId=1)

    result = model.create_or_update()

    assert result.id == 1
    mocks["create"].assert_called_once()
    mocks["perform_save"].assert_not_called()


def test_update_existing_instance(mocked_model):
    model, mocks = mocked_model
    cached_instance = TestModel(id=2, name="test", value=2, parentId=1)
    mocks["get_cached"].return_value = cached_instance
    model.value = 3  # This change should trigger an update
    mocks["perform_save"].return_value = TestModel(id=2, name="test", value=3, parentId=1)

    result = model.create_or_update()

    assert model._original_data == {
        "id": 2,
        "name": "test",
        "value": 2,
        "parentId": 1,
        "parentModule": "test_module",
    }, "Original data should be set to cached instance data"
    assert result.id == 2
    assert result.value == 3
    mocks["perform_save"].assert_called_once()
    assert model._original_data == {
        "id": 2,
        "name": "test",
        "value": 2,
        "parentId": 1,
        "parentModule": "test_module",
    }, "Original data should not change after save"


def test_no_update_when_no_changes(mocked_model):
    model, mocks = mocked_model
    cached_instance = TestModel(id=3, name="test", value=1, parentId=1)
    mocks["get_cached"].return_value = cached_instance

    result = model.create_or_update()

    mocks["get_cached"].assert_called_once()
    mocks["perform_save"].assert_not_called()

    assert result == cached_instance, "Should return the cached instance without changes"
    assert model._original_data == cached_instance.dict(
        exclude_unset=True
    ), "Original data should be set to cached instance data"

    print(f"Result: {result}")
    print(f"Cached instance: {cached_instance}")
    print(f"Model _original_data: {model._original_data}")


@pytest.mark.parametrize(
    "initial_value,new_value,expected_calls",
    [
        (1, 2, 1),  # Different value, should update
        (1, 1, 0),  # Same value, should not update
    ],
)
def test_update_behavior(mocked_model, initial_value, new_value, expected_calls):
    model, mocks = mocked_model
    cached_instance = TestModel(id=1, name="test", value=initial_value, parentId=1)
    mocks["get_cached"].return_value = cached_instance
    model.value = new_value
    mocks["perform_save"].return_value = TestModel(id=1, name="test", value=new_value, parentId=1)

    model.create_or_update()

    assert mocks["perform_save"].call_count == expected_calls


class TestFindByUnique:
    @pytest.fixture
    def mock_get_all_by_parent(self):
        with patch.object(TestModel, "get_all_by_parent") as mock:
            yield mock

    def test_find_by_unique_single_field_match(self, mock_get_all_by_parent):
        """Test finding an instance with a single unique field match"""
        instance = TestModel(name="test", value=1, parentId=1)
        existing = TestModel(id=1, name="test", value=2, parentId=1)
        mock_get_all_by_parent.return_value = [existing]

        result = instance.find_by_unique()

        assert result == existing
        mock_get_all_by_parent.assert_called_once_with(parent_id=1, parent_module="test_module")

    def test_find_by_unique_case_insensitive(self, mock_get_all_by_parent):
        """Test case-insensitive matching"""
        instance = TestModel(name="Test", value=1, parentId=1)
        existing = TestModel(id=1, name="test", value=2, parentId=1)
        mock_get_all_by_parent.return_value = [existing]

        result = instance.find_by_unique()

        assert result == existing

    def test_find_by_unique_no_match(self, mock_get_all_by_parent):
        """Test when no match is found"""
        instance = TestModel(name="test1", value=1, parentId=1)
        existing = TestModel(id=1, name="test2", value=2, parentId=1)
        mock_get_all_by_parent.return_value = [existing]

        result = instance.find_by_unique()

        assert result is None

    def test_find_by_unique_no_unique_fields(self):
        """Test when no unique fields are defined"""

        class NoUniqueModel(RegScaleModel):
            _unique_fields = []
            name: str

        instance = NoUniqueModel(name="test")

        with pytest.raises(NotImplementedError):
            instance.find_by_unique()

    def test_find_by_unique_no_parent_id(self):
        """Test when parent ID is missing"""
        instance = TestModel(name="test", value=1)  # No parentId

        with pytest.raises(ValueError):
            instance.find_by_unique()


class TestMultipleUniqueFields:
    @pytest.fixture
    def mock_get_all_by_parent(self):
        with patch.object(TestModelMultipleUnique, "get_all_by_parent") as mock:
            yield mock

    def test_find_by_unique_first_set_match(self, mock_get_all_by_parent):
        """Test matching on first set of unique fields"""
        instance = TestModelMultipleUnique(
            field1="test1",
            field2="test2",
            field3="different",  # Different value doesn't matter for first set match
            parentId=1,
        )
        existing = TestModelMultipleUnique(
            id=1,
            field1="test1",
            field2="test2",
            field3="also_different",  # Different value doesn't matter for first set match
            parentId=1,
        )
        mock_get_all_by_parent.return_value = [existing]

        result = instance.find_by_unique()

        # Should match because first set of unique fields matches
        assert result == existing

    def test_find_by_unique_second_set_match(self, mock_get_all_by_parent):
        """Test matching on second set of unique fields"""
        instance = TestModelMultipleUnique(
            field1="different1", field2="different2", field3="test3", parentId=1  # Matches on second set
        )
        existing = TestModelMultipleUnique(
            id=1, field1="test1", field2="test2", field3="test3", parentId=1  # Matches on second set
        )
        mock_get_all_by_parent.return_value = [existing]

        result = instance.find_by_unique()

        # Should match because second set of unique fields matches
        assert result == existing

    def test_find_by_unique_no_match(self, mock_get_all_by_parent):
        """Test when no unique field sets match"""
        instance = TestModelMultipleUnique(field1="different1", field2="different2", field3="different3", parentId=1)
        existing = TestModelMultipleUnique(id=1, field1="test1", field2="test2", field3="test3", parentId=1)
        mock_get_all_by_parent.return_value = [existing]

        result = instance.find_by_unique()

        # Should not match because no unique field sets match
        assert result is None

    def test_find_by_unique_with_none_values(self, mock_get_all_by_parent):
        """Test handling of None values in multiple unique fields"""
        instance = TestModelMultipleUnique(
            field1="test1", field2=None, field3="different3", parentId=1  # None in first set  # Different in second set
        )
        existing = TestModelMultipleUnique(
            id=1, field1="test1", field2=None, field3="test3", parentId=1  # None in first set
        )
        mock_get_all_by_parent.return_value = [existing]

        result = instance.find_by_unique()

        # Should not match because first set has None values and second set doesn't match
        assert result is None


class TestCaching:
    def test_cache_hit(self, mocked_model):
        """Test when object is found in cache"""
        model, mocks = mocked_model
        cached = TestModel(id=1, name="test", value=1, parentId=1)
        mocks["get_cached"].return_value = cached

        result = model.find_by_unique()

        assert result == cached
        mocks["get_cached"].assert_called_once()

    def test_cache_update_after_save(self, mocked_model):
        """Test that cache is updated after saving"""
        model, mocks = mocked_model
        updated = TestModel(id=1, name="test", value=2, parentId=1)
        mocks["perform_save"].return_value = updated

        model.value = 2
        model.create_or_update()

        mocks["cache"].assert_called_with(updated)


class TestErrorHandling:
    @pytest.fixture
    def mock_get_all_by_parent(self):
        with patch.object(TestModel, "get_all_by_parent") as mock:
            yield mock

    def test_create_or_update_with_api_error(self, mocked_model):
        """Test handling of API errors during create/update"""
        model, mocks = mocked_model
        mocks["get_cached"].return_value = None
        mocks["create"].side_effect = Exception("API Error")

        with pytest.raises(Exception) as exc_info:
            model.create_or_update()

        assert str(exc_info.value) == "API Error"

    @pytest.mark.parametrize("attribute_error_field", ["name", "value", "non_existent_field"])
    def test_find_by_unique_attribute_error(self, attribute_error_field, mocker):
        """Test handling of AttributeError during find_by_unique"""
        # Use mocker fixture instead of manual patch
        mock_get_all_by_parent = mocker.patch.object(TestModel, "get_all_by_parent")

        instance = TestModel(name="test", value=1, parentId=1)

        # Create a mock instance that will raise AttributeError for the specified field
        class MockTestModel(TestModel):
            def __getattr__(self, name):
                if name == attribute_error_field:
                    raise AttributeError(f"Mock object has no attribute '{name}'")
                return super().__getattr__(name)

        mock_instance = MockTestModel(name="test_value", value=1, parentId=1)
        mock_get_all_by_parent.return_value = [mock_instance]

        # Should not raise AttributeError
        result = instance.find_by_unique()
        assert result is None


class TestConcurrency:
    def test_concurrent_cache_access(self):
        """Test concurrent access to cache"""
        import threading
        import time

        model = TestModel(name="test", value=1, parentId=1)
        cache_key = model._get_cache_key(model)

        def cache_operation():
            with model._get_lock(cache_key):
                time.sleep(0.1)  # Simulate some work
                model.cache_object(model)

        threads = [threading.Thread(target=cache_operation) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Verify that cache operations completed without errors
        assert model.get_cached_object(cache_key) is not None


if __name__ == "__main__":
    pytest.main()
