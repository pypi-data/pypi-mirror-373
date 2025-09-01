from strenum import StrEnum


class InternalMemoryUnit(StrEnum):
    GIB = "gib"
    MIB = "mib"


class PurchaseOptionInternal(StrEnum):
    ONDEMAND = "ondemand"
    SPOT = "spot"


class InternalGpuType(StrEnum):
    NVIDIA_K80 = "nvidia_k80"
    NVIDIA_V100 = "nvidia_v100"
    NVIDIA_A100 = "nvidia_a100"
    NVIDIA_T4 = "nvidia_t4"
    NVIDIA_A10G = "nvidia_a10g"
    NVIDIA_L4 = "nvidia_l4"
    NVIDIA_T4_1_4_15 = "nvidia_t4_1_4_15"
    NVIDIA_T4_1_8_30 = "nvidia_t4_1_8_30"
    NVIDIA_T4_1_16_60 = "nvidia_t4_1_16_60"
    NVIDIA_A100_80GB_8_96_1360 = "nvidia_a100_80gb_8_96_1360"
    NVIDIA_V100_1_8_52 = "nvidia_v100_1_8_52"
    NVIDIA_V100_4_32_208 = "nvidia_v100_4_32_208"
