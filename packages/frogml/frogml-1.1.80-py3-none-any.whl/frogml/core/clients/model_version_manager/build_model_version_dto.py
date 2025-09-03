from typing import Optional, List
from pydantic import BaseModel, model_validator
from typing_extensions import Self

from frogml.core.clients.model_version_manager.const import (
    InternalMemoryUnit,
    PurchaseOptionInternal,
    InternalGpuType,
)
from frogml.core.exceptions import FrogmlException


class BuildPropertiesDTO(BaseModel):
    build_name: str = ""
    tags: List[str] = []
    gpu_compatible: bool = False


class DockerEnvDTO(BaseModel):
    base_image: str = ""
    cache: bool = True


class BuildEnvDTO(BaseModel):
    docker_env: Optional[DockerEnvDTO] = None


class TemplateSpecDTO(BaseModel):
    template_id: str


class CpuResourcesDTO(BaseModel):
    cpu: float
    memory_amount: int
    memory_units: Optional[InternalMemoryUnit]


class GpuResourcesDTO(BaseModel):
    gpu_type: Optional[InternalGpuType]
    gpu_amount: int


class PodResourcesDTO(BaseModel):
    template_spec: Optional[TemplateSpecDTO] = None
    cpu_resources: Optional[CpuResourcesDTO] = None
    gpu_resources: Optional[GpuResourcesDTO] = None

    @model_validator(mode="after")
    def _validate_pod_resources(self: Self) -> Self:
        """
        Validates that exactly one of the PodResourcesDTO fields is set.
        :raise FrogMLValidationError: If the validation fails.
        """
        fields_set = sum(
            [
                self.template_spec is not None,
                self.cpu_resources is not None,
                self.gpu_resources is not None,
            ]
        )

        if fields_set != 1:
            raise FrogmlException(
                "Exactly one of template_spec, cpu_resources, or gpu_resources must be set"
            )

        return self


class BuildConfigDTO(BaseModel):
    build_properties: Optional[BuildPropertiesDTO] = None
    build_env: Optional[BuildEnvDTO] = None
    pod_resources: PodResourcesDTO
    purchase_option: Optional[PurchaseOptionInternal] = None
    verbose: int = 3
    environment_id: str = ""
