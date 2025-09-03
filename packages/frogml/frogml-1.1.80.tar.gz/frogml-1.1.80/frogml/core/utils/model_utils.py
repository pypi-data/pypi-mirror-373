def get_model_id_from_model_name(model_name: str) -> str:
    return model_name.strip().lower().replace(" ", "_").replace("-", "_")
