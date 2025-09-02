import enum


class UnitPowerPerArea_V1_0_1_UnitCategories(str, enum.Enum):
    Unit_W_per_m2 = "W/m2"
    Unit_Btu_IT_per_h_ft2 = "Btu[IT]/(h.ft2)"
    Unit_Btu_IT_per_s_ft2 = "Btu[IT]/(s.ft2)"
    Unit_cal_th_per_h_cm2 = "cal[th]/(h.cm2)"
    Unit_hp_per_in2 = "hp/in2"
    Unit_hp_hyd_per_in2 = "hp[hyd]/in2"
    Unit_kW_per_cm2 = "kW/cm2"
    Unit_kW_per_m2 = "kW/m2"
    Unit_mW_per_m2 = "mW/m2"
    Unit_ucal_th_per_s_cm2 = "ucal[th]/(s.cm2)"
    Unit_W_per_cm2 = "W/cm2"
    Unit_W_per_mm2 = "W/mm2"
