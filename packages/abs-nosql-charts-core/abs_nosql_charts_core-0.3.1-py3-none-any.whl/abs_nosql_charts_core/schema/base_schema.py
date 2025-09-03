from enum import Enum
from pydantic import BaseModel, Field, model_validator, ValidationError
from datetime import datetime
from typing import Optional, Dict, Any, List, Union, Literal
from abs_nosql_repository_core.schema.base_schema import BaseSchema, FilterSchema, SortDirection, SortSchema
from .charts_schema import (
    NumberChartDataSchema,
    LineChartDataSchema,
    BarChartDataSchema,
    PieChartDataSchema,
    ColumnChartDataSchema,
    ScatterChartDataSchema,
    CandlestickChartDataSchema,
    TableChartDataSchema,
    AggregationType,
)

from .charts_schema import (
    TopN,
    BinningSpec
)

class ChartType(str, Enum):
    NUMBER = "number"
    BAR = "bar"
    STACKED_BAR = "stacked_bar"
    STACKED_BAR_100 = "stacked_bar_100"
    COLUMN = "column"
    STACKED_COLUMN = "stacked_column"
    STACKED_COLUMN_100 = "stacked_column_100"
    LINE = "line"
    AREA = "area"
    PIE = "pie"
    DONUT = "donut"
    GAUGE = "gauge"
    SCATTER = "scatter"
    TABLE = "table"
    CANDLESTICK = "candlestick"


class AggregationSpec(BaseModel):
    field: str
    type: AggregationType
    alias: str


class TopNSpec(TopN):
    field: str = Field(..., description="Field to rank by (should match an aggregation field alias)")


class AggregationBinningSpec(BinningSpec):
    field: str = Field(..., description="Field to apply binning to")
    alias: Optional[str] = Field(
        default=None, 
        description="Alias for the binned field. If None, uses original field name"
    )


class ChartAggregation(BaseModel):
    group_by: Optional[list[str]] = Field(
        default_factory=list,
        description="Fields to group by"
    )
    aggregation_fields: Optional[List[AggregationSpec]] = None
    binning_specs: Optional[List[AggregationBinningSpec]] = Field(
        default=None,
        description="Binning specifications for fields before grouping"
    )
    top_n: Optional[TopNSpec] = Field(
        default=None, 
        description="Specification for top N results based on aggregated values"
    )
    sort_by: Optional[List[SortSchema]] = Field(
        default=None,
        description="Sort order for groups (columns)"
    )



# ------------------------------ Customizations (Not used yet) ------------------------------


# String field customization
class StringFieldCustomization(BaseModel):
    custom_label: Optional[str] = Field(default=None, description="Custom label for string field")

class DecimalFormatting(BaseModel):
    enabled: bool = Field(default=False, description="Whether decimal formatting is enabled")
    value: Optional[float] = Field(default=None, description="Value to format")

class multiplierFormatting(BaseModel):
    enabled: bool = Field(default=False, description="Whether multiplier formatting is enabled")
    value: Optional[float] = Field(default=None, description="Value to format")

class prefixFormatting(BaseModel):
    enabled: bool = Field(default=False, description="Whether prefix formatting is enabled")
    value: Optional[str] = Field(default=None, description="Value to format")

class suffixFormatting(BaseModel):
    enabled: bool = Field(default=False, description="Whether suffix formatting is enabled")
    value: Optional[str] = Field(default=None, description="Value to format")


class NumberFormatting(BaseModel):
    decimals: Optional[DecimalFormatting] = Field(default=None, description="Number of decimal places")
    multiplier: Optional[multiplierFormatting] = Field(default=None, description="Multiplier for the value")
    prefix: Optional[prefixFormatting] = Field(default=None, description="Prefix for the value")
    suffix: Optional[suffixFormatting] = Field(default=None, description="Suffix for the value")

class NumberFieldCustomization(BaseModel):
    number_formatting: Optional[NumberFormatting] = Field(default=None)

# Date field customization
class DateFieldCustomization(BaseModel):
    date_format: Optional[str] = Field(default=None, description="Date format string, e.g., 'MMM-YYYY', 'MMMM YYYY', etc.")
    custom_label: Optional[str] = Field(default=None, description="Custom label for date field")

# Union for field customizations
FieldCustomizationType = Union[StringFieldCustomization, NumberFieldCustomization, DateFieldCustomization]

class FieldCustomization(BaseModel):
    field_type: Literal["x", "y", "series", "number", "label", "date"]
    settings: FieldCustomizationType

class ChartCustomizationSchema(BaseModel):
    fields: Optional[List[FieldCustomization]] = Field(default_factory=list, description="Customizations for individual fields (x, y, number, etc.)")




# ----------------------------- Chart Schema -----------------------------

class ReferenceData(BaseModel):
    fields: Optional[list[str]] = Field(default=None, description="Fields to include in the reference")
    record_ids: Optional[list[str]] = Field(default=None, description="Record ids to include in the reference")

BaseChartDataSchema = Union[
    NumberChartDataSchema,
    LineChartDataSchema,
    BarChartDataSchema,
    ColumnChartDataSchema,
    PieChartDataSchema,
    ScatterChartDataSchema,
    CandlestickChartDataSchema,
    TableChartDataSchema
]


class BaseChartSchema(BaseModel):
    chart_type: ChartType = Field(..., description="Type of the chart, e.g., 'Number', 'Bar', 'Line', etc.")
    data: BaseChartDataSchema = Field(..., description="Data configuration for the chart (x, y, number, etc.)")
    filters: Optional[FilterSchema] = Field(default=None, description="List of filters applied to the chart")
    customizations: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Customizations for the chart")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Meta information for the chart")

    @model_validator(mode="before")
    def validate_data_by_type(cls, values):
        chart_type = values.get("chart_type")
        data = values.get("data")
        type_to_schema = {
            "number": NumberChartDataSchema,
            "line": LineChartDataSchema,
            "area": LineChartDataSchema,
            "bar": BarChartDataSchema,
            "stacked_bar": BarChartDataSchema,
            "stacked_bar_100": BarChartDataSchema,
            "column": ColumnChartDataSchema,
            "stacked_column": ColumnChartDataSchema,
            "stacked_column_100": ColumnChartDataSchema,
            "pie": PieChartDataSchema,
            "donut": PieChartDataSchema,
            "gauge": PieChartDataSchema,
            "scatter": ScatterChartDataSchema,
            "candlestick": CandlestickChartDataSchema,
            "table": TableChartDataSchema
        }
        schema_cls = type_to_schema.get(chart_type)
        if schema_cls and data is not None and not isinstance(data, schema_cls):
            try:
                values["data"] = schema_cls(**data) if isinstance(data, dict) else schema_cls.parse_obj(data)
            except Exception as e:
                raise Exception(f"Invalid data for chart_type {chart_type}: {e}")
        return values

    class Config:
        arbitrary_types_allowed = True



