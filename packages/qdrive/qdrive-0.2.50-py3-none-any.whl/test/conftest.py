import typing, uuid

import pytest

from etiket_client.remote.endpoints.scope import scope_list, scope_create
from etiket_client.remote.endpoints.models.scope import ScopeCreate, ScopeRead
from etiket_client.remote.endpoints.S3 import s3_bucket_read

def _get_default_bucket_uuid() -> uuid.UUID:
    buckets = s3_bucket_read()
    if not buckets:
        raise RuntimeError("No S3 buckets available for scope creation.")
    print(buckets)
    return buckets[0].bucket_uuid


def _ensure_scope(name: str, description: str | None = None, bucket_uuid: uuid.UUID | None = None) -> ScopeRead:
    existing: typing.List[ScopeRead] = scope_list(name_query=name)
    if len(existing) > 1:
        raise RuntimeError(f"Multiple scopes with name '{name}' found.")
    if existing:
        return existing[0]

    bucket_uuid = bucket_uuid or _get_default_bucket_uuid()
    scope_create(ScopeCreate(name=name, uuid=uuid.uuid4(),
                                description=description or f"Test scope '{name}'",
                                bucket_uuid=bucket_uuid))
    # Read back to return the created scope
    created: typing.List[ScopeRead] = scope_list(name_query=name)
    if not created:
        raise RuntimeError(f"Failed to create or read back scope '{name}'.")
    return created[0]

@pytest.fixture(scope="session")
def test_scopes() -> tuple[ScopeRead, ScopeRead, ScopeRead]:
    """
    Ensure three test scopes exist for the session and return them.

    Returns:
        Tuple[ScopeRead, ScopeRead, ScopeRead]: (unit_test_scope_1, unit_test_scope_2, unit_test_scope_3)
    """
    default_bucket_uuid = _get_default_bucket_uuid()
    unit_test_scope_1 = _ensure_scope("unit_test_scope_1", description="Scope for unit tests", bucket_uuid=default_bucket_uuid)
    unit_test_scope_2 = _ensure_scope("unit_test_scope_2", description="Scope for unit tests", bucket_uuid=default_bucket_uuid)
    unit_test_scope_3 = _ensure_scope("unit_test_scope_3", description="Scope for unit tests", bucket_uuid=default_bucket_uuid)
    return unit_test_scope_1, unit_test_scope_2, unit_test_scope_3


