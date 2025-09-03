from typing import List, Optional

from pydantic.v1 import Field, root_validator, validator, BaseModel

from bigeye_sdk.model.protobuf_enum_facade import (
    SimpleDbtTestToMetricType,
    SimpleAggregationType,
)
from bigeye_sdk.model.protobuf_message_facade import (
    SimpleMetricDefinition,
    SimplePredefinedMetric,
    SimpleMetricParameter,
    SimpleConstantThreshold,
    SimpleTemplateMetric,
)

relationships_test_names = [
    "relationships",
    "referential integrity",
    "referential integrity check",
]
relationships_template = """{{ column_to_check }} in (SELECT DISTINCT {{ lookup_column }} FROM {{ lookup_table }})"""


class SimpleDbtColumn(BaseModel):
    type: str = "column"
    name: str = ""
    description: Optional[str] = None
    tests: Optional[List[SimpleMetricDefinition]] = Field(default_factory=lambda: [])

    @root_validator(pre=True)
    def validate_tests(cls, values):
        tests = []
        if values.get("tests"):
            for test in values["tests"]:
                params = [SimpleMetricParameter(key="arg1", column_name=values["name"])]
                if isinstance(test, dict) and list(test.keys())[0] == "accepted_values":
                    params.append(
                        SimpleMetricParameter(
                            key="list",
                            string_value=",".join(test["accepted_values"]["values"]),
                        )
                    )
                    t = SimpleDbtTestToMetricType.accepted_values
                    name = "dbt_test_accepted_values"
                    mt = SimplePredefinedMetric(predefined_metric=t.value)
                    threshold = SimpleConstantThreshold(
                        type="CONSTANT", upper_bound=1, lower_bound=1
                    )
                elif isinstance(test, dict) and list(test.keys())[0] == "relationships":
                    column_to_check = params.pop()
                    column_to_check.key = "column_to_check"
                    params.extend(
                        [
                            column_to_check,
                            SimpleMetricParameter(
                                key="lookup_column",
                                string_value=test["relationships"]["field"],
                            ),
                            SimpleMetricParameter(
                                key="lookup_table",
                                string_value=test["relationships"]["to"][5:-2],
                            ),
                        ]
                    )
                    name = "dbt_test_relationships"
                    threshold = SimpleConstantThreshold(
                        type="CONSTANT", upper_bound=1, lower_bound=1
                    )
                    mt = SimpleTemplateMetric(
                        template_id=0, aggregation_type=SimpleAggregationType.PERCENT
                    )
                elif test in SimpleDbtTestToMetricType.__members__:
                    t = SimpleDbtTestToMetricType[test.lower()]
                    name = f"dbt_test_{test.lower()}"
                    threshold = SimpleConstantThreshold(
                        type="CONSTANT", upper_bound=0, lower_bound=0
                    )
                    mt = SimplePredefinedMetric(predefined_metric=t.value)

                else:
                    """Not supported."""
                    continue

                smd = SimpleMetricDefinition(
                    metric_type=mt,
                    metric_name=name,
                    description="Converted from dbt schema file",
                    parameters=params,
                    threshold=threshold,
                )
                tests.append(smd)

            values["tests"] = tests
        return values


class SimpleDbtModel(BaseModel):
    type: str = "model"
    name: str = ""
    description: Optional[str] = None
    columns: Optional[List[SimpleDbtColumn]] = Field(default_factory=lambda: [])
    column_tests: Optional[List[SimpleMetricDefinition]] = Field(
        default_factory=lambda: []
    )

    @validator("column_tests", always=True)
    def add_model_tests(cls, field_value, values):
        if values["columns"]:
            cols = values["columns"]
            for c in cols:
                field_value.extend(c.tests)

        return field_value


class SimpleDbtSchema(BaseModel):
    type: str = "schema"
    version: int = 0
    models: List[SimpleDbtModel] = Field(default_factory=lambda: [])
