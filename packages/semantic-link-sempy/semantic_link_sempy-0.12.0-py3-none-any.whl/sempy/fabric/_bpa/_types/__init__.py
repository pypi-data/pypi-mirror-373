from enum import Enum

import sempy._utils._icons as icons


class Field(Enum):
    RELATIONSHIP = "Relationship"
    COLUMN = "Column"
    MEASURE = "Measure"
    HIERARCHY = "Hierarchy"
    TABLE = "Table"
    ROLE = "Role"
    MODEL = "Model"
    CALCULATION_ITEM = "Calculation Item"
    CALCULATED_COLUMN = "Calculated Column"
    CALCULATED_TABLE = "Calculated Table"
    ROW_LEVEL_SECURITY = "Row Level Security"
    PARTITION = "Partition"


class Category(Enum):
    PERFORMANCE = "Performance"
    SCHEMA = "Schema"
    DESIGN = "Design"
    ERROR_PREVENTION = "Error Prevention"
    DAX_EXPRESSIONS = "DAX Expressions"
    NAMING_CONVENTIONS = "Naming Conventions"
    MAINTENANCE = "Maintenance"
    FORMATTING = "Formatting"


class Severity(Enum):
    INFO = icons.info
    WARNING = icons.warning
    ERROR = icons.error
