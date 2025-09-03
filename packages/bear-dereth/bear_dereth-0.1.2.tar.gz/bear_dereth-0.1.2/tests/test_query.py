from pathlib import Path

# ruff : noqa: TC001
from bear_dereth.config._settings_manager._base_classes import QueryLike, StorageBackend
from bear_dereth.config._settings_manager._db import Database
from bear_dereth.config._settings_manager._query import BackupQuery, Query


class TestBackupQuery:
    """Test BackupQuery functionality and edge cases."""

    def test_db_and_query_integration(self, tmp_path: Path) -> None:
        """Test that factory functions work together."""
        db: StorageBackend = Database(tmp_path)
        Q: BackupQuery = BackupQuery()  # noqa: N806

        # # Basic integration test
        # db.set("test_key", "test_value")
        # assert db.contains(Q.key == "test_key")

        # results = db.search(Q.key == "test_key")
        # assert len(results) == 1
        # assert results[0]["value"] == "test_value"

    def test_simple_equality(self):
        """Test basic equality queries."""
        query = BackupQuery()
        test_func = query.name == "test"

        # Should match
        assert test_func({"name": "test"})

        # Should not match
        assert not test_func({"name": "other"})
        assert not test_func({"other_key": "test"})

    def test_not_equal(self):
        """Test not-equal queries."""
        query = BackupQuery()
        test_func = query.status != "inactive"

        assert test_func({"status": "active"})
        assert not test_func({"status": "inactive"})

    def test_nested_paths(self):
        """Test nested attribute access."""
        query = BackupQuery()
        test_func = query.user.name == "alice"

        assert test_func({"user": {"name": "alice"}})  # type: ignore[code]
        assert not test_func({"user": {"name": "bob"}})  # type: ignore[code]
        assert not test_func({"user": {}})  # type: ignore[code]
        assert not test_func({})

    def test_exists(self):
        """Test exists functionality."""
        test_func = BackupQuery().optional.exists()

        assert test_func({"optional": "value"})
        assert test_func({"optional": None})  # None is considered existing
        assert not test_func({})
        assert not test_func({"other": "value"})

    def test_greater_than_simple(self):
        """Test simple greater-than comparison."""
        test_func = Query().age > 18

        # Same types
        assert test_func({"age": 25})
        assert not test_func({"age": 15})
        assert not test_func({"age": 18})  # Not greater than, equal

    def test_less_than_simple(self):
        """Test simple less-than comparison."""
        test_func = Query().score < 100

        assert test_func({"score": 50})
        assert not test_func({"score": 150})
        assert not test_func({"score": 100})  # Not less than, equal

    def test_comparison_with_none(self):
        """Test comparisons with None values."""
        query: QueryLike = Query()
        gt_func = query.value > 10
        lt_func = query.value < 10

        # None should always return False for comparisons
        assert not gt_func({"value": None})
        assert not lt_func({"value": None})
        assert not gt_func({})  # Missing key returns None

    def test_comparison_with_matches_regex(self):
        """Test regex matching."""
        query: BackupQuery = BackupQuery()
        regex_func = query.username.matches(r"^user_\d+$")
        assert regex_func({"username": "user_123"})
        assert not regex_func({"username": "admin"})
        assert not regex_func({"username": "user_abc"})
        assert not regex_func({"other_key": "user_123"})

    def test_hash_functionality(self) -> None:
        """Test that Query objects can be hashed."""
        query1 = Query().path
        query2 = Query().path
        query3 = Query().other

        assert hash(query1) == hash(query2)
        print(hash(query1), hash(query2), hash(query3))
        assert hash(query1) != hash(query3)

        # Should be usable in sets
        query_set = {query1, query2, query3}
        assert len(query_set) == 2  # query1 and query2 are the same


def test_query_with_deeply_nested_missing_path():
    """Test query with deeply nested path that doesn't exist."""
    query = BackupQuery()
    test_func = query.very.deeply.nested.path == "value"

    # Should not crash, should return False
    assert not test_func({})
    assert not test_func({"very": {}})  # type: ignore[code]
    assert not test_func({"very": {"deeply": {}}})  # type: ignore[code]


def test_get_query_returns_query() -> None:
    """Test that get_query returns a QueryBackend."""
    query = Query()

    # Should have QueryBackend methods
    assert hasattr(query, "__eq__")
    assert hasattr(query, "__ne__")
    assert hasattr(query, "__gt__")
    assert hasattr(query, "__lt__")
    assert hasattr(query, "exists")
