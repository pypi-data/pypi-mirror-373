"""
Constants for the Xplainable client.
"""

URL_PREFIX = "/v1"

# Authentication endpoints
AUTH_ENDPOINTS = {
    "connect": f"{URL_PREFIX}/client/connect",
}

# Model endpoints
MODEL_ENDPOINTS = {
    "create": f"{URL_PREFIX}/client/models/create",
    "add_version": f"{URL_PREFIX}/client/models/add-version",
    "list_team_models": f"{URL_PREFIX}/client/models/teams",
    "get_model": f"{URL_PREFIX}/client/models/{{model_id}}",
    "list_versions": f"{URL_PREFIX}/client/models/versions/{{model_id}}",
    "list_partitions": f"{URL_PREFIX}/client/models/partitions/{{version_id}}",
    "link_preprocessor": f"{URL_PREFIX}/client/preprocessors/link-preprocessor",
}

# Deployment endpoints
DEPLOYMENT_ENDPOINTS = {
    "create": f"{URL_PREFIX}/client/deployments/create",
    "create_deploy_key": f"{URL_PREFIX}/client/deployments/create-deploy-key",
    "list_team_deployments": f"{URL_PREFIX}/client/deployments/teams/{{team_id}}",
    "list_deploy_keys": f"{URL_PREFIX}/client/deployments/{{deployment_id}}",
    "list_active_team_keys": f"{URL_PREFIX}/client/deployments/teams/{{team_id}}/active-keys",
    "revoke_key": f"{URL_PREFIX}/client/deployments/revoke-key",
    "delete": f"{URL_PREFIX}/client/deployments/{{deployment_id}}",
    "activate": f"{URL_PREFIX}/client/deployments/{{deployment_id}}/activate",
    "deactivate": f"{URL_PREFIX}/client/deployments/{{deployment_id}}/deactivate",
    "payload": f"{URL_PREFIX}/client-deployments/{{deployment_id}}/payload",
}

# Preprocessor endpoints
PREPROCESSOR_ENDPOINTS = {
    "create": f"{URL_PREFIX}/client/preprocessors/create",
    "add_version": f"{URL_PREFIX}/client/preprocessors/add",
    "update_version": f"{URL_PREFIX}/client/preprocessors/update-version",
    "list_team_preprocessors": f"{URL_PREFIX}/client/preprocessors/teams/{{team_id}}",
    "get": f"{URL_PREFIX}/client/preprocessors/{{preprocessor_id}}",
    "get_version": f"{URL_PREFIX}/client/preprocessors/versions/{{version_id}}",
    "apply": f"{URL_PREFIX}/client/preprocessors/versions/apply",
    "download": f"{URL_PREFIX}/client/preprocessors/versions/download",
    
    # New endpoints for pipeline objects (business logic moved to API)
    "create_from_pipeline": f"{URL_PREFIX}/client/preprocessors/create-from-pipeline",
    "add_version_from_pipeline": f"{URL_PREFIX}/client/preprocessors/add-version-from-pipeline",
    "update_version_from_pipeline": f"{URL_PREFIX}/client/preprocessors/update-version-from-pipeline",
    "load_pipeline": f"{URL_PREFIX}/client/preprocessors/load-pipeline/{{version_id}}",
    "list": f"{URL_PREFIX}/client/preprocessors",
}

# Collection endpoints
COLLECTION_ENDPOINTS = {
    "create": f"{URL_PREFIX}/client/collections/create",
    "get_model_collections": f"{URL_PREFIX}/client/collections/model/{{model_id}}",
    "get_team_collections": f"{URL_PREFIX}/client/collections/team",
    "get_team_collections_by_id": f"{URL_PREFIX}/client/collections/team/{{team_id}}",
    "get_collection": f"{URL_PREFIX}/client/collections/{{collection_id}}",
    "update_name": f"{URL_PREFIX}/client/collections/{{collection_id}}/name",
    "update_description": f"{URL_PREFIX}/client/collections/{{collection_id}}/description",
    "delete": f"{URL_PREFIX}/client/collections/{{collection_id}}",
    "create_scenarios": f"{URL_PREFIX}/client/collections/{{collection_id}}/scenarios",
    "get_scenarios": f"{URL_PREFIX}/client/collections/{{collection_id}}/scenarios",
    "get_scenario": f"{URL_PREFIX}/client/collections/scenarios/{{scenario_id}}",
    "delete_scenario": f"{URL_PREFIX}/client/collections/scenarios/{{scenario_id}}",
}

# Inference endpoints
INFERENCE_ENDPOINTS = {
    "predict": f"{URL_PREFIX}/predict",
}

# Autotrain endpoints
AUTOTRAIN_ENDPOINTS = {
    "summarize": f"{URL_PREFIX}/client/autotrain/summarize",
    "generate_goals": f"{URL_PREFIX}/client/autotrain/generate_goals",
    "generate_labels": f"{URL_PREFIX}/client/autotrain/generate_labels",
    "generate_feature_engineering": f"{URL_PREFIX}/client/autotrain/generate_feature_engineering",
    "start_autotrain": f"{URL_PREFIX}/client/autotrain/start_autotrain",
    "check_training_status": f"{URL_PREFIX}/client/autotrain/check_training_status",
    "train_manual": f"{URL_PREFIX}/client/autotrain/train_manual",
}

# GPT endpoints
GPT_ENDPOINTS = {
    "generate_report": f"{URL_PREFIX}/client/models/report/generate",
    "explain_model": f"{URL_PREFIX}/client/models/explain",
}

# Combine all endpoints for backward compatibility
URL_PATHS = {
    **AUTH_ENDPOINTS,
    **{f"models_{k}": v for k, v in MODEL_ENDPOINTS.items()},
    **{f"deployments_{k}": v for k, v in DEPLOYMENT_ENDPOINTS.items()},
    **{f"preprocessors_{k}": v for k, v in PREPROCESSOR_ENDPOINTS.items()},
    **{f"collections_{k}": v for k, v in COLLECTION_ENDPOINTS.items()},
    **AUTOTRAIN_ENDPOINTS,
    **GPT_ENDPOINTS,
}