from typing import List, Optional, Any

from pydantic import BaseModel, Field

from bigeye_sdk.functions.schema_change_functions import (
    is_deleted_dataset,
    is_deleted_schema,
    is_created_schema,
    is_created_dataset,
    is_deleted_field,
    is_created_field,
    is_changed_field,
)
from bigeye_sdk.generated.com.bigeye.models.generated import SchemaChange

collapsible = \
    """
<details>
  <summary><h2>{source_name} schema changes</h2></summary>
  
{details}
</details>
    """


class SourceSchemaChange(BaseModel):
    msg: str = "{header}\n{fields}\n{datasets}\n{schemas}"
    added: str = "{type_added}<br>{added}</br>"
    deleted: str = "{type_deleted}<br>{deleted}</br>"
    changed: str = "<h3>Fields changed:</h3><br>{fields_changed}</br>"
    field_has_changed_from: str = "{name} has changed from {old_type} to {new_type}"

    name: str
    changes: List[SchemaChange]
    source_header: str = ""
    schemas_added: Optional[List[str]] = Field(default_factory=lambda: [])
    schemas_deleted: Optional[List[str]] = Field(default_factory=lambda: [])
    datasets_added: Optional[List[str]] = Field(default_factory=lambda: [])
    datasets_deleted: Optional[List[str]] = Field(default_factory=lambda: [])
    fields_added: Optional[List[str]] = Field(default_factory=lambda: [])
    fields_deleted: Optional[List[str]] = Field(default_factory=lambda: [])
    fields_changed: Optional[List[str]] = Field(default_factory=lambda: [])

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.group_changes()
        self.source_header = (
            f"The following changes have occurred in Bigeye source {self.name}:\n"
        )

    def group_changes(self):
        for change in self.changes:
            if is_deleted_schema(change=change):
                self.schemas_deleted.append(change.fully_qualified_name)
            elif is_created_schema(change=change):
                self.schemas_added.append(change.fully_qualified_name)
            elif is_deleted_dataset(change=change):
                self.datasets_deleted.append(change.fully_qualified_name)
            elif is_created_dataset(change=change):
                self.datasets_added.append(change.fully_qualified_name)
            elif is_deleted_field(change=change):
                self.fields_deleted.append(change.fully_qualified_name)
            elif is_created_field(change=change):
                self.fields_added.append(change.fully_qualified_name)
            elif is_changed_field(change=change):
                changed = self.field_has_changed_from.format(
                    name=change.fully_qualified_name,
                    old_type=change.old_value,
                    new_type=change.new_value,
                )
                self.fields_changed.append(changed)

    def format_message(self):
        fields = f"{self.format_field_changes()}<br>{self.format_added_fields()}</br><br>{self.format_deleted_fields()}</br>"
        datasets = f"<br>{self.format_added_datasets()}</br><br>{self.format_deleted_datasets()}</br>"
        schemas = f"<br>{self.format_added_schemas()}</br><br>{self.format_deleted_schemas()}</br>"

        summary = self.msg.format(
            header="", fields=fields, datasets=datasets, schemas=schemas
        )
        return collapsible.format(source_name=self.name, details=summary)

    def format_webhook(self):
        return {
            self.name: {
                "fields": {
                    "changed": self.fields_changed,
                    "added": self.fields_added,
                    "deleted": self.fields_deleted,
                },
                "datasets": {
                    "added": self.datasets_added,
                    "deleted": self.datasets_deleted,
                },
                "schemas": {
                    "added": self.schemas_added,
                    "deleted": self.schemas_deleted,
                }
            }
        }

    def format_field_changes(self):
        return (
            "<li>" + self.changed.format(fields_changed="</br><br>".join(self.fields_changed)) + "</li>"
            if self.fields_changed
            else ""
        )

    def format_added_fields(self) -> str:
        return ("<li>" +
                self.added.format(
                    type_added="<h3>Fields added:</h3>", added="</br><br>".join(self.fields_added)
                ) + "</li>"
                if self.fields_added
                else ""
                )

    def format_deleted_fields(self):
        return ("<li>" +
                self.deleted.format(
                    type_deleted="<h3>Fields deleted:</h3>",
                    deleted="</br><br>".join(self.fields_deleted),
                ) + "</li>"
                if self.fields_deleted
                else ""
                )

    def format_added_datasets(self):
        return ("<li>" +
                self.added.format(
                    type_added="<h3>Datasets added:</h3>", added="</br><br>".join(self.datasets_added)
                ) + "</li>"
                if self.datasets_added
                else ""
                )

    def format_deleted_datasets(self):
        return ("<li>" +
                self.deleted.format(
                    type_deleted="<h3>Datasets deleted:</h3>",
                    deleted="</br><br>".join(self.datasets_deleted),
                ) + "</li>"
                if self.datasets_deleted
                else ""
                )

    def format_added_schemas(self):
        return ("<li>" +
                self.added.format(
                    type_added="<h3>Schemas added:</h3>", added="</br><br>".join(self.schemas_added)
                ) + "</li>"
                if self.schemas_added
                else ""
                )

    def format_deleted_schemas(self):
        return ("<li>" +
                self.deleted.format(
                    type_deleted="<h3>Schemas deleted:</h3>",
                    deleted="</br><br>".join(self.schemas_deleted),
                ) + "</li>"
                if self.schemas_deleted
                else ""
                )
