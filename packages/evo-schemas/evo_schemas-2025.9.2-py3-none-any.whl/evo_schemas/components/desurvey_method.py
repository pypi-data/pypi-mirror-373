import enum


class DesurveyMethod_V1_0_0(str, enum.Enum):
    ENUM_MINIMUM_CURVATURE = "minimum_curvature"
    ENUM_BALANCED_TANGENT = "balanced_tangent"
    ENUM_TRENCH = "trench"
