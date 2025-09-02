import enum


class UnitSpecificHeatCapacity_V1_0_1_UnitCategories(str, enum.Enum):
    Unit_J_per_kg_deltaK = "J/(kg.deltaK)"
    Unit_Btu_IT_per_lbm_deltaF = "Btu[IT]/(lbm.deltaF)"
    Unit_Btu_IT_per_lbm_deltaR = "Btu[IT]/(lbm.deltaR)"
    Unit_cal_th_per_g_deltaK = "cal[th]/(g.deltaK)"
    Unit_J_per_g_deltaK = "J/(g.deltaK)"
    Unit_kcal_th_per_kg_deltaC = "kcal[th]/(kg.deltaC)"
    Unit_kJ_per_kg_deltaK = "kJ/(kg.deltaK)"
    Unit_kW_h_per_kg_deltaC = "kW.h/(kg.deltaC)"
