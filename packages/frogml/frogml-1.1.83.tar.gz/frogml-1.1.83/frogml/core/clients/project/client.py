from typing import Optional

import grpc
from dependency_injector.wiring import Provide, inject

from frogml._proto.qwak.projects.jfrog_project_spec_pb2 import ModelRepositoryJFrogSpec
from frogml._proto.qwak.projects.projects_pb2 import (
    CreateProjectRequest,
    DeleteProjectRequest,
    GetProjectRequest,
    ListProjectsRequest,
)
from frogml._proto.qwak.projects.projects_pb2_grpc import ProjectsManagementServiceStub
from frogml.core.exceptions import FrogmlException
from frogml.core.inner.di_configuration import FrogmlContainer


class ProjectsManagementClient:
    """
    Used for interacting with Project Management endpoints
    """

    @inject
    def __init__(self, grpc_channel=Provide[FrogmlContainer.core_grpc_channel]):
        self._projects_management_service = ProjectsManagementServiceStub(grpc_channel)

    def list_projects(self):
        try:
            return self._projects_management_service.ListProjects(ListProjectsRequest())

        except grpc.RpcError as e:
            raise FrogmlException(f"Failed to list projects, error is {e.details()}")

    def create_project(
        self,
        project_name: str,
        project_description: str,
        jfrog_project_key: Optional[str] = None,
    ):
        try:
            return self._projects_management_service.CreateProject(
                CreateProjectRequest(
                    project_name=project_name,
                    project_description=project_description,
                    jfrog_spec=ModelRepositoryJFrogSpec(
                        jfrog_project_key=jfrog_project_key,
                    ),
                )
            )

        except grpc.RpcError as e:
            raise FrogmlException(f"Failed to create project, error is {e.details()}")

    def delete_project(self, project_id):
        try:
            return self._projects_management_service.DeleteProject(
                DeleteProjectRequest(project_id=project_id)
            )

        except grpc.RpcError as e:
            raise FrogmlException(f"Failed to delete project, error is {e.details()}")

    def get_project(self, project_id: str = "", project_name: str = ""):
        try:
            return self._projects_management_service.GetProject(
                GetProjectRequest(project_id=project_id, project_name=project_name)
            )

        except grpc.RpcError as e:
            raise FrogmlException(
                f"Failed to fetch models associated with project id {project_id}, error is {e.details()}"
            )
