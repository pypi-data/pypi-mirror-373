import enum


class UnitMassPerTimePerArea_V1_0_1_UnitCategories(str, enum.Enum):
    Unit_kg_per_m2_s = "kg/(m2.s)"
    Unit_g_ft_per_cm3_s = "g.ft/(cm3.s)"
    Unit_g_m_per_cm3_s = "g.m/(cm3.s)"
    Unit_kPa_s_per_m = "kPa.s/m"
    Unit_lbm_per_ft2_h = "lbm/(ft2.h)"
    Unit_lbm_per_ft2_s = "lbm/(ft2.s)"
    Unit_MPa_s_per_m = "MPa.s/m"
