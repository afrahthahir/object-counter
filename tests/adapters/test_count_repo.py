import pytest
from sqlalchemy import create_engine
from counter.adapters.count_repo import CountPostgresRepo, ObjectCountEntity, Base
from counter.domain.models import ObjectCount

"""
Integration tests for the SQLAlchemy-based CountPostgresRepo.
Uses in-memory SQLite to verify the SQL logic without external dependencies.
"""

@pytest.fixture
def sqlite_repo():
    """Initializes a clean in-memory SQlite database for each test."""
    repo = CountPostgresRepo("sqlite:///:memory:")
    return repo

def test_sqlite_repo_updates_and_reads_values(sqlite_repo):
    """Verifies that new object counts can be saved and retrieved accurately."""
    assert sqlite_repo.read_values() == []

    new_counts = [ObjectCount("cat", 2), ObjectCount("dog", 1)]
    sqlite_repo.update_values(new_counts)

    results = sqlite_repo.read_values()
    assert len(results) == 2
    cat_count = next(c for c in results if c.object_class == "cat")
    assert cat_count.count == 2

def test_sqlite_repo_increments_existing_values(sqlite_repo):
    """Verifies the 'upsert' logic: existing records should have their counts incremented."""
    sqlite_repo.update_values([ObjectCount("cat", 2)])
    sqlite_repo.update_values([ObjectCount("cat", 3)])

    results = sqlite_repo.read_values(["cat"])
    assert results[0].count == 5

def test_sqlite_repo_filters_by_class(sqlite_repo):
    """Verifies that the repository correctly filters results by object class name."""
    sqlite_repo.update_values([
        ObjectCount("cat", 10),
        ObjectCount("dog", 5),
        ObjectCount("bird", 2)
    ])

    results = sqlite_repo.read_values(["cat", "bird"])
    assert len(results) == 2
    classes = [c.object_class for c in results]
    assert "cat" in classes
    assert "bird" in classes
    assert "dog" not in classes
