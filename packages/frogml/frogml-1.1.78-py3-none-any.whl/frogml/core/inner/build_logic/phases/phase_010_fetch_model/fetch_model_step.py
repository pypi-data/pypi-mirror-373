from __future__ import annotations

from frogml.core.inner.build_logic.constants.temp_dir import TEMP_LOCAL_MODEL_DIR
from frogml.core.inner.build_logic.interface.step_inteface import Step

from .fetch_strategy_manager.fetch_strategy_manager import FetchStrategyManager


class FetchModelStep(Step):
    STEP_DESCRIPTION = "Fetch model code"

    def description(self) -> str:
        return self.STEP_DESCRIPTION

    def execute(self) -> None:
        fetch_strategy_manager = FetchStrategyManager(
            uri=self.config.build_properties.model_uri.uri,
            build_logger=self.build_logger,
        )
        self.build_logger.debug("Fetching model code")
        git_commit_id = fetch_strategy_manager.fetch(
            dest=self.context.host_temp_local_build_dir / TEMP_LOCAL_MODEL_DIR,
            git_branch=self.config.build_properties.model_uri.git_branch,
            git_credentials=self.context.git_credentials,
            model_id=self.config.build_properties.model_id,
            build_id=self.context.build_id,
            custom_dependencies_path=self.config.build_env.python_env.dependency_file_path,
            main_dir=self.config.build_properties.model_uri.main_dir,
            dependency_path=self.context.model_relative_dependency_file,
            lock_dependency_path=self.context.model_relative_dependency_lock_file,
            dependency_required_folders=self.config.build_properties.model_uri.dependency_required_folders,
            git_ssh_key=self.context.git_ssh_key,
        )
        if git_commit_id:
            self.context.git_commit_id = git_commit_id
            self.build_logger.debug(f"Git commit ID identified - {git_commit_id}")

        self.build_logger.debug(
            f"Model code stored in {self.context.host_temp_local_build_dir / TEMP_LOCAL_MODEL_DIR}"
        )
        self.build_logger.info("Successfully fetched model code")
