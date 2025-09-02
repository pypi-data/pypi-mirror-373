import enum


class UnitReciprocalTemperature_V1_0_1_UnitCategories(str, enum.Enum):
    Unit_1_per_deltaC = "1/deltaC"
    Unit_1_per_deltaF = "1/deltaF"
    Unit_1_per_deltaR = "1/deltaR"
    Unit_1_per_deltaK = "1/deltaK"
    Unit_m_per_m_deltaK = "m/(m.deltaK)"
    Unit_m3_per_m3_deltaK = "m3/(m3.deltaK)"
    Unit_in_per_in_deltaF = "in/(in.deltaF)"
    Unit_mm_per_mm_deltaK = "mm/(mm.deltaK)"
    Unit_1EMinus6_m3_per_m3_deltaC = "1E-6 m3/(m3.deltaC)"
    Unit_1EMinus6_m3_per_m3_deltaF = "1E-6 m3/(m3.deltaF)"
    Unit_ppm_vol_per_deltaC = "ppm[vol]/deltaC"
    Unit_ppm_vol_per_deltaF = "ppm[vol]/deltaF"
