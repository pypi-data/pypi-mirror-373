import enum


class UnitHeatTransferCoefficient_V1_0_1_UnitCategories(str, enum.Enum):
    Unit_W_per_m2_deltaK = "W/(m2.deltaK)"
    Unit_Btu_IT_per_h_ft2_deltaF = "Btu[IT]/(h.ft2.deltaF)"
    Unit_Btu_IT_per_h_ft2_deltaR = "Btu[IT]/(h.ft2.deltaR)"
    Unit_Btu_IT_per_h_m2_deltaC = "Btu[IT]/(h.m2.deltaC)"
    Unit_Btu_IT_per_s_ft2_deltaF = "Btu[IT]/(s.ft2.deltaF)"
    Unit_cal_th_per_h_cm2_deltaC = "cal[th]/(h.cm2.deltaC)"
    Unit_cal_th_per_s_cm2_deltaC = "cal[th]/(s.cm2.deltaC)"
    Unit_J_per_s_m2_deltaC = "J/(s.m2.deltaC)"
    Unit_kcal_th_per_h_m2_deltaC = "kcal[th]/(h.m2.deltaC)"
    Unit_kJ_per_h_m2_deltaK = "kJ/(h.m2.deltaK)"
    Unit_kW_per_m2_deltaK = "kW/(m2.deltaK)"
