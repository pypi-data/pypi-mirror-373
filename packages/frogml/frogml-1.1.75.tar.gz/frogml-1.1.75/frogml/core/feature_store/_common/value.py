UPDATE_FROGML_SDK_WITH_FEATURE_STORE_EXTRA_MSG = (
    'please run: pip install -U "frogml-sdk[feature-store]"'
)


def missing_pyspark_exception_message(name: str) -> str:
    return (
        f"Missing 'pyspark' dependency required for {name} transformation. "
        f"{UPDATE_FROGML_SDK_WITH_FEATURE_STORE_EXTRA_MSG}"
    )
