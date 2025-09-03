DUPLICATE_SAVED_METRIC_ID_EXISTS_ERRMSG = "Duplicate saved_metric_id: '{saved_metric_id}' has multiple definitions."
SAVED_METRIC_ID_NOT_EXISTS_IN_SAVED_METRICS_DEFINITION_ERRMSG = \
    "Undefined saved_metric_id: '{saved_metric_id}' does not exist in saved_metric_definitions."
DUPLICATE_TAG_EXISTS_ERRMSG = "Duplicate tag_id: '{tag_id}' has multiple definitions."
TAG_ID_NOT_EXISTS_IN_TAG_DEFINITION_ERRMSG = "Undefined tag_id: '{tag_id}' does not exist in tag_definitions."
FQ_COL_NOT_RESOLVES_TO_COLUMN_ERRMSG = "Invalid column_selector: '{fq_column_name}' does not resolve to a column. Names " \
                                       "must have either 4 elements or 5 elements.  For example: " \
                                       "source.schema.table.column OR " \
                                       "source.database.schema.table.column.  Wild cards are accepted."
WILD_CARDS_NOT_SUPPORT_IN_FQ_TABLE_NAMES_ERRMSG = \
    "Invalid fq_table_name: '{fq_table_name}' is not valid; wildcards are not supported."
FQ_TABLE_NAME_MUST_RESOLVE_TO_TABLE_ERRMSG = "Invalid fq_table_name: '{fq_table_name}' does not resolve to a table.  Names " \
                                             "must have either 3 elements or 4 elements.  For example: " \
                                             "source.schema.table OR " \
                                             "source.database.schema.table."
SRC_NOT_EXISTS_FOR_DEPLOYMENT_ERRMSG = "Invalid source: '{fq_name}' does not exist in workspace."
FORMATTING_ERRMSG = "Invalid formatting: {s}"
OVERRIDE_METRIC_TYPE_SAVED_METRIC_ERRMSG = \
    "Invalid metric configuration: Cannot override the metric_type in a saved_metric_definition: {config_error_lines}"
MUST_HAVE_METRIC_TYPE_ERRMSG = "Invalid metric configuration: definition must include metric type {config_error_lines}"
MUST_HAVE_METRIC_ID_ERRMSG = "Each Saved Metric Definition must contain a saved_metric_id.  " \
                             "Saved Metric: {config_error_lines}"
METRIC_TYPE_NOT_EXISTS_ERRMSG = "Invalid metric: {metric} does not exist. {match_message}"
INVALID_DECLARED_ATTRIBUTE_ERRMSG = "Invalid attribute: '{err_attrib}' is not a valid attribute in {cls_name}. {match_message}"
POSSIBLE_MATCH_ERRMSG = "Try '{possible_matches}' instead."
NO_POSSIBLE_MATCH_ERRMSG = " "
INVALID_OBJECT_TYPE_ERRMSG = "Invalid Object Type: {data_type} not a supported supported type. {match_message}"
OBJECT_HAS_NO_TYPE_ERRMSG = "Object requires a type declaration but one was not provided."
METRIC_APPLICATION_ERROR = "Invalid Metric Application: {errmsg}"
INVALID_OBJECT_ERRMSG = "Invalid Object: {cls} does not contain an object matching the attributes passed.  {object}"
UNKNOWN_SERIALIZATION_ERROR = "Unknown Serialization Error: value could not be serialized.  Raw value: {raw_value}"
TWO_SCHEDULES_DEFINED = "Both schedule frequency and metric schedule are defined. Please choose one."
MISMATCHED_ATTRIBUTE_ACROSS_MULTIPLE_FILES = \
    "Mismatched attribute {attribute}: This value must be consistent across files."
MUST_HAVE_COLUMN_SELECTOR_NAME_OR_TYPE = "Invalid column_selector: '{column_selector}'. Column selectors must have " \
                                         "either a name or a type specified, not just an exclusion. "
COLUMN_SELECTOR_MUST_HAVE_VALID_REGEX = "Invalid regex for column_selector. Regular expression fails to compile with " \
                                        "given error. {error_message}"
NAME_AND_EXCLUDE_MUST_NOT_BE_DECLARED_IF_REGEX = "Invalid column_selector: '{column_selector}'.\nRegex selectors " \
                                                 "cannot be provided in addition to name and exclude selectors. " \
                                                 "Please choose either regex or name selectors."
INVALID_THRESHOLD_BOUNDS = "Invalid threshold bounds. Both upper_bound_only and lower_bound_only are set to true."
