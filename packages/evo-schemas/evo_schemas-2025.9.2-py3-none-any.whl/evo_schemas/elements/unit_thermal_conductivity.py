import enum


class UnitThermalConductivity_V1_0_1_UnitCategories(str, enum.Enum):
    Unit_J_m_per_s_m2_deltaK = "J.m/(s.m2.deltaK)"
    Unit_W_per_m_deltaK = "W/(m.deltaK)"
    Unit_Btu_IT_in_per_h_ft2_deltaF = "Btu[IT].in/(h.ft2.deltaF)"
    Unit_kJ_m_per_h_m2_deltaK = "kJ.m/(h.m2.deltaK)"
    Unit_Btu_IT_per_h_ft_deltaF = "Btu[IT]/(h.ft.deltaF)"
    Unit_cal_th_per_h_cm_deltaC = "cal[th]/(h.cm.deltaC)"
    Unit_cal_th_per_s_cm_deltaC = "cal[th]/(s.cm.deltaC)"
    Unit_kcal_th_per_h_m_deltaC = "kcal[th]/(h.m.deltaC)"
