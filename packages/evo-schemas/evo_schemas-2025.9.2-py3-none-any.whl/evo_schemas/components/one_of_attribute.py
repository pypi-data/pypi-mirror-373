from .bool_attribute import BoolAttribute_V1_0_1, BoolAttribute_V1_1_0
from .bool_time_series import BoolTimeSeries_V1_0_1, BoolTimeSeries_V1_1_0
from .category_attribute import CategoryAttribute_V1_0_1, CategoryAttribute_V1_1_0
from .category_ensemble import CategoryEnsemble_V1_0_1, CategoryEnsemble_V1_1_0
from .category_time_series import CategoryTimeSeries_V1_0_1, CategoryTimeSeries_V1_1_0
from .color_attribute import ColorAttribute_V1_0_0, ColorAttribute_V1_1_0
from .continuous_attribute import ContinuousAttribute_V1_0_1, ContinuousAttribute_V1_1_0
from .continuous_ensemble import ContinuousEnsemble_V1_0_1, ContinuousEnsemble_V1_1_0
from .continuous_time_series import ContinuousTimeSeries_V1_0_1, ContinuousTimeSeries_V1_1_0
from .date_time_attribute import DateTimeAttribute_V1_0_1, DateTimeAttribute_V1_1_0
from .indices_attribute import IndicesAttribute_V1_0_1, IndicesAttribute_V1_1_0
from .integer_attribute import IntegerAttribute_V1_0_1, IntegerAttribute_V1_1_0
from .string_attribute import StringAttribute_V1_0_1, StringAttribute_V1_1_0
from .vector_attribute import VectorAttribute_V1_0_0

OneOfAttribute_V1_2_0_Item = (
    BoolAttribute_V1_1_0
    | ContinuousAttribute_V1_1_0
    | ContinuousEnsemble_V1_1_0
    | VectorAttribute_V1_0_0
    | CategoryAttribute_V1_1_0
    | CategoryEnsemble_V1_1_0
    | DateTimeAttribute_V1_1_0
    | StringAttribute_V1_1_0
    | BoolTimeSeries_V1_1_0
    | ContinuousTimeSeries_V1_1_0
    | CategoryTimeSeries_V1_1_0
    | ColorAttribute_V1_1_0
    | IntegerAttribute_V1_1_0
    | IndicesAttribute_V1_1_0
)
OneOfAttribute_V1_2_0 = list[OneOfAttribute_V1_2_0_Item]
OneOfAttribute_V1_0_1_Item = (
    BoolAttribute_V1_0_1
    | ContinuousAttribute_V1_0_1
    | ContinuousEnsemble_V1_0_1
    | CategoryAttribute_V1_0_1
    | CategoryEnsemble_V1_0_1
    | DateTimeAttribute_V1_0_1
    | StringAttribute_V1_0_1
    | BoolTimeSeries_V1_0_1
    | CategoryTimeSeries_V1_0_1
    | ContinuousTimeSeries_V1_0_1
)
OneOfAttribute_V1_0_1 = list[OneOfAttribute_V1_0_1_Item]
OneOfAttribute_V1_1_0_Item = (
    BoolAttribute_V1_0_1
    | ContinuousAttribute_V1_0_1
    | ContinuousEnsemble_V1_0_1
    | CategoryAttribute_V1_0_1
    | CategoryEnsemble_V1_0_1
    | DateTimeAttribute_V1_0_1
    | StringAttribute_V1_0_1
    | BoolTimeSeries_V1_0_1
    | CategoryTimeSeries_V1_0_1
    | ContinuousTimeSeries_V1_0_1
    | ColorAttribute_V1_0_0
    | IntegerAttribute_V1_0_1
    | IndicesAttribute_V1_0_1
)
OneOfAttribute_V1_1_0 = list[OneOfAttribute_V1_1_0_Item]
