import enum


class UnitThermalInsulance_V1_0_1_UnitCategories(str, enum.Enum):
    Unit_deltaC_m2_h_per_kcal_th = "deltaC.m2.h/kcal[th]"
    Unit_deltaF_ft2_h_per_Btu_IT = "deltaF.ft2.h/Btu[IT]"
    Unit_deltaK_m2_per_kW = "deltaK.m2/kW"
    Unit_deltaK_m2_per_W = "deltaK.m2/W"
