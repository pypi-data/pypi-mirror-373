from typing import Optional

from frogml._proto.jfml.model_version.v1.build_spec_pb2 import (
    BuildSpec,
    BuildProperties,
    DockerEnv,
    BuildEnv,
)
from frogml._proto.qwak.fitness_service.fitness_pb2 import PurchaseOption
from frogml._proto.qwak.user_application.common.v0.resources_pb2 import (
    CpuResources,
    GpuResources,
    GpuType,
    MemoryUnit,
    PodComputeResourceTemplateSpec,
)
from frogml.core.clients.model_version_manager.build_model_version_dto import (
    BuildConfigDTO,
)
from frogml.core.clients.model_version_manager.const import (
    InternalMemoryUnit,
    PurchaseOptionInternal,
    InternalGpuType,
)


def map_build_conf_to_build_spec(build_conf: BuildConfigDTO) -> BuildSpec:
    build_model_version_spec = BuildSpec(
        build_properties=(
            BuildProperties(
                build_name=build_conf.build_properties.build_name,
                tags=build_conf.build_properties.tags,
                gpu_compatible=build_conf.build_properties.gpu_compatible,
            )
            if build_conf.build_properties
            else None
        ),
        build_env=(
            BuildEnv(
                docker_env=DockerEnv(
                    base_image=build_conf.build_env.docker_env.base_image,
                    no_cache=not build_conf.build_env.docker_env.cache,
                )
            )
            if build_conf.build_env and build_conf.build_env.docker_env
            else None
        ),
        verbose=build_conf.verbose,
        environment_id=build_conf.environment_id,
        purchase_option=_map_purchase_option(
            purchase_option=build_conf.purchase_option
        ),
    )

    if build_conf.pod_resources.template_spec:
        build_model_version_spec.pod_resources.template_spec.CopyFrom(
            PodComputeResourceTemplateSpec(
                template_id=build_conf.pod_resources.template_spec.template_id
            )
        )

    elif build_conf.pod_resources.cpu_resources:
        build_model_version_spec.pod_resources.cpu_resources.CopyFrom(
            CpuResources(
                cpu=build_conf.pod_resources.cpu_resources.cpu,
                memory_amount=build_conf.pod_resources.cpu_resources.memory_amount,
                memory_units=_map_memory_units(
                    memory_unit=build_conf.pod_resources.cpu_resources.memory_units
                ),
            )
        )

    elif build_conf.pod_resources.gpu_resources:
        build_model_version_spec.pod_resources.gpu_resources.CopyFrom(
            GpuResources(
                gpu_type=_map_gpu_type(
                    gpu_type=build_conf.pod_resources.gpu_resources.gpu_type
                ),
                gpu_amount=build_conf.pod_resources.gpu_resources.gpu_amount,
            )
        )

    return build_model_version_spec


def _map_memory_units(
    memory_unit: Optional[InternalMemoryUnit] = None,
) -> MemoryUnit.ValueType:
    if memory_unit == InternalMemoryUnit.MIB:
        return MemoryUnit.MIB
    elif memory_unit == InternalMemoryUnit.GIB:
        return MemoryUnit.GIB

    return MemoryUnit.INVALID_MEMORY_UNIT


def _map_purchase_option(
    purchase_option: Optional[PurchaseOptionInternal] = None,
) -> PurchaseOption.ValueType:
    if purchase_option == PurchaseOptionInternal.ONDEMAND:
        return PurchaseOption.ONDEMAND_PURCHASE_OPTION
    elif purchase_option == PurchaseOptionInternal.SPOT:
        return PurchaseOption.SPOT_PURCHASE_OPTION

    return PurchaseOption.INVALID_PURCHASE_OPTION


def _map_gpu_type(gpu_type: Optional[InternalGpuType] = None) -> GpuType.ValueType:
    if gpu_type == InternalGpuType.NVIDIA_K80:
        return GpuType.NVIDIA_K80
    elif gpu_type == InternalGpuType.NVIDIA_V100:
        return GpuType.NVIDIA_V100
    elif gpu_type == InternalGpuType.NVIDIA_A100:
        return GpuType.NVIDIA_A100
    elif gpu_type == InternalGpuType.NVIDIA_T4:
        return GpuType.NVIDIA_T4
    elif gpu_type == InternalGpuType.NVIDIA_A10G:
        return GpuType.NVIDIA_A10G
    elif gpu_type == InternalGpuType.NVIDIA_L4:
        return GpuType.NVIDIA_L4
    elif gpu_type == InternalGpuType.NVIDIA_T4_1_4_15:
        return GpuType.NVIDIA_T4_1_4_15
    elif gpu_type == InternalGpuType.NVIDIA_T4_1_8_30:
        return GpuType.NVIDIA_T4_1_8_30
    elif gpu_type == InternalGpuType.NVIDIA_T4_1_16_60:
        return GpuType.NVIDIA_T4_1_16_60
    elif gpu_type == InternalGpuType.NVIDIA_A100_80GB_8_96_1360:
        return GpuType.NVIDIA_A100_80GB_8_96_1360
    elif gpu_type == InternalGpuType.NVIDIA_V100_1_8_52:
        return GpuType.NVIDIA_V100_1_8_52
    elif gpu_type == InternalGpuType.NVIDIA_V100_4_32_208:
        return GpuType.NVIDIA_V100_4_32_208
    return GpuType.INVALID_GPU_TYPE
