from enum import Enum
from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from typing import Optional, List, Union
from abs_nosql_repository_core.schema.base_schema import SortDirection

class FieldTypeEnum(str, Enum):
    INT = "int"
    DATE = "date"
    TIMESTAMP = "timestamp"
    DATETIME = "datetime"
    STR = "str"
    STRING = "string"
    TEXT = "text"
    NUMBER = "number"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"
    FLOAT = "float"
    DECIMAL = "decimal"
    ARRAY = "array"
    DROPDOWN = "dropdown"
    RADIO = "radio"
    CHECKBOX = "checkbox"
    URL = "url"
    ASSOCIATION = "association"
    USER = "user"


class AggregationType(str, Enum):
    SUM = "sum"
    AVG = "avg"
    COUNT = "count"
    MAX = "max"
    MIN = "min"
    DISTINCT = "distinct"
    VARIANCE = "variance"
    STD_DEV = "std_dev"
    FIRST = "first"
    LAST = "last"

# ------------------------------ Data Settings ------------------------------

class TopN(BaseModel):
    value: Optional[int] = Field(default=None, description="Value for top N")
    others : Optional[bool] = Field(default=False, description="Show others as one group")

class IntValueOptions(BaseModel):
    value: Optional[int] = Field(default=None, description="A single integer value")
    

class DateValueOptions(BaseModel):
    granularity: Optional[str] = Field(default=None, description="Granularity for date fields: 'year', 'month', 'week', 'day', 'hour', 'minute', etc.")
    start_date: Optional[datetime] = Field(default=None, description="Start date for date binning")
    end_date: Optional[datetime] = Field(default=None, description="End date for date binning")
    timezone: Optional[str] = Field(default="UTC", description="Timezone for date operation")

class StrValueLabelGroup(BaseModel):
    label: str = Field(..., description="Label for the group of string values")
    values: List[str] = Field(..., description="List of string values for this label")

class StrValueOptions(BaseModel):
    groups: List[StrValueLabelGroup] = Field(..., description="List of label groups for string values")

ValueOptionsType = Union[IntValueOptions, DateValueOptions, StrValueOptions]

class BinningSpec(BaseModel):
    enabled: bool = Field(default=False, description="Whether binning is enabled for this field")
    bin_value: Optional[ValueOptionsType] = Field(default=None, 
                                                    description="Options for binning, depending on the field type (int, date, str, etc.)")
    
    @model_validator(mode='before')
    def validate_bin_value(cls, values):
        if not isinstance(values, dict):
            values = values.model_dump()

        bin_value = values.get('bin_value', None)
        
        if bin_value and isinstance(bin_value, dict):
            # Determine type based on field name or content
            if 'granularity' in bin_value:
                values['bin_value'] = DateValueOptions(**bin_value)
            elif 'groups' in bin_value:
                values['bin_value'] = StrValueOptions(**bin_value)
            else:
                values['bin_value'] = IntValueOptions(**bin_value)
        return values
    

# ------------------------------ Number Chart Data Config ------------------------------

class NumberChartFieldSpec(BaseModel):
    field: str = Field(..., description="Field name from the dataset")
    field_type: Optional[str] = Field(default=None, description="Field type")
    aggregation: AggregationType = Field(..., description="Aggregation type to apply (required for number chart)")
    label: Optional[str] = Field(default=None, description="Label override for the field")


# ------------------------------ Bar Chart Data Config ------------------------------

class BarChartXFieldSpec(BaseModel):
    field: str = Field(..., description="Field name from the dataset")
    field_type: Optional[FieldTypeEnum] = Field(default=None, description="Field type")
    aggregation:AggregationType = Field(..., description="Aggregation type to apply (required for bar chart x)")
    label: Optional[str] = Field(default=None, description="Label override for the field")
    
class BarChartYFieldSpec(BaseModel):
    field: str = Field(..., description="Field name from the dataset")
    field_type: Optional[FieldTypeEnum] = Field(default=None, description="Field type")
    binning: Optional[BinningSpec] = Field(default=None, description="Binning specification for the field")
    label: Optional[str] = Field(default=None, description="Label override for the field")
    top_n: Optional[TopN] = Field(default=None, description="Top N specification for the field")
    sort_by: Optional[SortDirection] = Field(default=None, description="Sort by specification for the field")

class BarChartGroupByFieldSpec(BaseModel):
    field: str = Field(..., description="Field for series grouping")
    field_type: Optional[FieldTypeEnum] = Field(default=None, description="Field type")
    binning: Optional[BinningSpec] = Field(default=None, description="Binning specification for the series field")
    label: Optional[str] = Field(default=None, description="Label override for the field")


# ------------------------------ Column Chart Data Config ------------------------------

class ColumnChartYFieldSpec(BaseModel):
    field: str = Field(..., description="Field name from the dataset")
    field_type: Optional[FieldTypeEnum] = Field(default=None, description="Field type")
    aggregation: AggregationType = Field(..., description="Aggregation type to apply (required for bar chart x)")
    label: Optional[str] = Field(default=None, description="Label override for the field")
    
class ColumnChartXFieldSpec(BaseModel):
    field: str = Field(..., description="Field name from the dataset")
    field_type: Optional[FieldTypeEnum] = Field(default=None, description="Field type")
    binning: Optional[BinningSpec] = Field(default=None, description="Binning specification for the field")
    label: Optional[str] = Field(default=None, description="Label override for the field")
    top_n: Optional[TopN] = Field(default=None, description="Top N specification for the field")
    sort_by: Optional[SortDirection] = Field(default=None, description="Sort by specification for the field")

class ColumnChartGroupByFieldSpec(BaseModel):
    field: str = Field(..., description="Field for series grouping")
    field_type: Optional[FieldTypeEnum] = Field(default=None, description="Field type")
    binning: Optional[BinningSpec] = Field(default=None, description="Binning specification for the series field")
    label: Optional[str] = Field(default=None, description="Label override for the field")


# ------------------------------ Line Chart Data Config ------------------------------

class LineChartXFieldSpec(BaseModel):
    field: str = Field(..., description="Field name from the dataset")
    field_type: Optional[FieldTypeEnum] = Field(default=None, description="Field type")
    label: Optional[str] = Field(default=None, description="Label override for the field")
    binning: Optional[BinningSpec] = Field(default=None, description="Binning specification for the field")
    sort_by: Optional[SortDirection] = Field(default=None, description="Sort by specification for the field")
    top_n: Optional[TopN] = Field(default=None, description="Top N specification for the field")

class LineChartYFieldSpec(BaseModel):
    field: str = Field(..., description="Field name for y value")
    field_type: Optional[FieldTypeEnum] = Field(default=None, description="Field type")
    label: Optional[str] = Field(default=None, description="Label override for the field")
    aggregation: Optional[AggregationType] = Field(default=None, description="Aggregation type to apply (required for line chart)")

class LineChartGroupByFieldSpec(BaseModel):
    field: str = Field(..., description="Field name for series grouping")
    field_type: Optional[FieldTypeEnum] = Field(default=None, description="Field type")
    binning: Optional[BinningSpec] = Field(default=None, description="Binning specification for the series field")
    label: Optional[str] = Field(default=None, description="Label override for the field")


# ------------------------------ Pie Chart Data Config ------------------------------

class PieChartGroupByFieldSpec(BaseModel):
    field: str = Field(..., description="Field name from the dataset")
    field_type: Optional[FieldTypeEnum] = Field(default=None, description="Field type")
    label: Optional[str] = Field(default=None, description="Label override for the field")
    binning: Optional[BinningSpec] = Field(default=None, description="Binning specification for the field")
    sort_by: Optional[SortDirection] = Field(default=None, description="Sort by specification for the field")
    top_n: Optional[TopN] = Field(default=None, description="Top N specification for the field")

class PieChartValueFieldSpec(BaseModel):
    field: str = Field(..., description="Field name from the dataset")
    field_type: Optional[FieldTypeEnum] = Field(default=None, description="Field type")
    label: Optional[str] = Field(default=None, description="Label override for the field")
    aggregation: AggregationType = Field(..., description="Aggregation type to apply (required for pie chart)")


# ------------------------------ Scatter Chart Data Config ------------------------------

class ScatterChartXFieldSpec(BaseModel):
    field: str = Field(..., description="Field name from the dataset")
    field_type: Optional[FieldTypeEnum] = Field(default=None, description="Field type")
    label: Optional[str] = Field(default=None, description="Label override for the field")

class ScatterChartYFieldSpec(BaseModel):
    field: str = Field(..., description="Field name from the dataset")
    field_type: Optional[FieldTypeEnum] = Field(default=None, description="Field type")
    label: Optional[str] = Field(default=None, description="Label override for the field")


# ------------------------------ Candlestick Chart Data Config ------------------------------

class CandlestickChartXFieldSpec(BaseModel):
    field: str = Field(..., description="Field name from the dataset")
    field_type: Optional[FieldTypeEnum] = Field(default=None, description="Field type")
    label: Optional[str] = Field(default=None, description="Label override for the field")
    binning: Optional[BinningSpec] = Field(default=None, description="Binning specification for the field")
    sort_by: Optional[SortDirection] = Field(default=None, description="Sort by specification for the field")
    top_n: Optional[TopN] = Field(default=None, description="Top N specification for the field")

class CandlestickChartHighSpec(BaseModel):
    field: str = Field(..., description="Field name from the dataset")
    field_type: Optional[FieldTypeEnum] = Field(default=None, description="Field type")
    label: Optional[str] = Field(default=None, description="Label override for the field")

class CandlestickChartLowSpec(BaseModel):
    field: str = Field(..., description="Field name from the dataset")
    field_type: Optional[FieldTypeEnum] = Field(default=None, description="Field type")
    label: Optional[str] = Field(default=None, description="Label override for the field")
    
class CandlestickChartOpenSpec(BaseModel):
    field: str = Field(..., description="Field name from the dataset")
    field_type: Optional[FieldTypeEnum] = Field(default=None, description="Field type")
    label: Optional[str] = Field(default=None, description="Label override for the field")

class CandlestickChartCloseSpec(BaseModel):
    field: str = Field(..., description="Field name from the dataset")
    field_type: Optional[FieldTypeEnum] = Field(default=None, description="Field type")
    label: Optional[str] = Field(default=None, description="Label override for the field")
    

# ------------------------------ Table Chart Data Config ------------------------------

class TableChartGroupSchema(BaseModel):
    field: str = Field(..., description="Field name from the dataset")
    field_type: Optional[FieldTypeEnum] = Field(default=None, description="Field type")
    label: Optional[str] = Field(default=None, description="Label override for the field")
    binning: Optional[BinningSpec] = Field(default=None, description="Binning specification for the field")

class TableChartValueSchema(BaseModel):
    field: str = Field(..., description="Field name from the dataset")
    field_type: Optional[FieldTypeEnum] = Field(default=None, description="Field type")
    label: Optional[str] = Field(default=None, description="Label override for the field")
    aggregation: AggregationType = Field(..., description="Aggregation type to apply (required for table chart)")



# ------------------------------ Main Charts Data Schemas ------------------------------

class NumberChartDataSchema(BaseModel):
    number: NumberChartFieldSpec

class BarChartDataSchema(BaseModel):
    x: List[BarChartXFieldSpec]
    y: BarChartYFieldSpec
    group_by: Optional[BarChartGroupByFieldSpec] = None

class LineChartDataSchema(BaseModel):
    x: LineChartXFieldSpec
    y: List[LineChartYFieldSpec]
    group_by: Optional[LineChartGroupByFieldSpec] = None

class ColumnChartDataSchema(BaseModel):
    x: ColumnChartXFieldSpec
    y: List[ColumnChartYFieldSpec]
    group_by: Optional[ColumnChartGroupByFieldSpec] = None

class PieChartDataSchema(BaseModel):
    group_by: PieChartGroupByFieldSpec
    value: PieChartValueFieldSpec


class ScatterChartDataSchema(BaseModel):
    x: ScatterChartXFieldSpec
    y: ScatterChartYFieldSpec


class CandlestickChartDataSchema(BaseModel):
    x: CandlestickChartXFieldSpec
    high: CandlestickChartHighSpec
    low: CandlestickChartLowSpec
    open: CandlestickChartOpenSpec
    close: CandlestickChartCloseSpec


class TableChartDataSchema(BaseModel):
    limit: Optional[int] = Field(default=20, description="Limit the number of records to return")
    page: Optional[int] = Field(default=1, description="Page number for pagination (1-based)")
    total: Optional[bool] = Field(default=False, description="Whether to include totals row in the table")
    groups: List[TableChartGroupSchema]
    values: List[TableChartValueSchema]


