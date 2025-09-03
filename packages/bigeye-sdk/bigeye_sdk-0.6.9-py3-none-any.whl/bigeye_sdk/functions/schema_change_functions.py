from bigeye_sdk.generated.com.bigeye.models.generated import (
    SchemaChange,
    SchemaChangeOperation,
    CatalogEntityType,
)


def is_deleted_schema(change: SchemaChange) -> bool:
    return (
        change.change_type == SchemaChangeOperation.SCHEMA_CHANGE_OPERATION_DELETED
        and change.object_type == CatalogEntityType.CATALOG_ENTITY_TYPE_SCHEMA
    )


def is_created_schema(change: SchemaChange) -> bool:
    return (
        change.change_type == SchemaChangeOperation.SCHEMA_CHANGE_OPERATION_CREATED
        and change.object_type == CatalogEntityType.CATALOG_ENTITY_TYPE_SCHEMA
    )


def is_deleted_dataset(change: SchemaChange) -> bool:
    return (
        change.change_type == SchemaChangeOperation.SCHEMA_CHANGE_OPERATION_DELETED
        and change.object_type == CatalogEntityType.CATALOG_ENTITY_TYPE_DATASET
    )


def is_created_dataset(change: SchemaChange) -> bool:
    return (
        change.change_type == SchemaChangeOperation.SCHEMA_CHANGE_OPERATION_CREATED
        and change.object_type == CatalogEntityType.CATALOG_ENTITY_TYPE_DATASET
    )


def is_deleted_field(change: SchemaChange) -> bool:
    return (
        change.change_type == SchemaChangeOperation.SCHEMA_CHANGE_OPERATION_DELETED
        and change.object_type == CatalogEntityType.CATALOG_ENTITY_TYPE_FIELD
    )


def is_created_field(change: SchemaChange) -> bool:
    return (
        change.change_type == SchemaChangeOperation.SCHEMA_CHANGE_OPERATION_CREATED
        and change.object_type == CatalogEntityType.CATALOG_ENTITY_TYPE_FIELD
    )


def is_changed_field(change: SchemaChange) -> bool:
    return (
        change.change_type == SchemaChangeOperation.SCHEMA_CHANGE_OPERATION_TYPE_CHANGED
        and change.object_type == CatalogEntityType.CATALOG_ENTITY_TYPE_FIELD
    )

