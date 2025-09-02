import enum


class UnitCurrency_V1_0_1_UnitCategories(str, enum.Enum):
    Unit_dollars = "$"
    Unit_dollars_per_t = "$/t"
    Unit_dollars_per_ton_US = "$/ton[US]"
