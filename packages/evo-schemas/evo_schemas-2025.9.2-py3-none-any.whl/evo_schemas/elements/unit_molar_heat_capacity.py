import enum


class UnitMolarHeatCapacity_V1_0_1_UnitCategories(str, enum.Enum):
    Unit_J_per_mol_deltaK = "J/(mol.deltaK)"
    Unit_Btu_IT_per_lbmol_deltaF = "Btu[IT]/(lbmol.deltaF)"
    Unit_cal_th_per_mol_deltaC = "cal[th]/(mol.deltaC)"
    Unit_kJ_per_kmol_deltaK = "kJ/(kmol.deltaK)"
