import importlib.metadata
import platform


class Recorder:
    @staticmethod
    def get_environment_dependencies():
        distributions = importlib.metadata.distributions()
        return sorted(
            [f"{dist.metadata['Name']}=={dist.version}" for dist in distributions]
        )

    @staticmethod
    def get_environment_details():
        return [
            f"arch={platform.architecture()[0]}",
            f"cpu={platform.processor()}",
            f"platform={platform.platform()}",
            f"python_version={platform.python_version()}",
            f"python_implementation={platform.python_implementation()}",
            f"python_compiler={platform.python_compiler()}",
        ]
