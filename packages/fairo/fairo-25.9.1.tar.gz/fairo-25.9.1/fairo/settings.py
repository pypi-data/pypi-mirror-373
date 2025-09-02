import os


def get_fairo_api_key():
    return os.getenv('FAIRO_API_ACCESS_KEY_ID', None)


def get_fairo_api_secret():
    return os.getenv('FAIRO_API_SECRET', None)


def get_fairo_base_url():
    return os.getenv('FAIRO_BASE_URL', "https://api.fairo.ai/api/v1")


# Databricks
# MLFlow configuration
def get_mlflow_user():
    return os.getenv('MLFLOW_TRACKING_USERNAME', os.getenv('FAIRO_API_ACCESS_KEY_ID', None))


def get_mlflow_server():
    return os.getenv('MLFLOW_TRACKING_SERVER', "https://mlflow.fairo.ai")


def get_mlflow_password():
    return os.getenv('MLFLOW_TRACKING_PASSWORD', os.getenv('FAIRO_API_SECRET', None))


def get_mlflow_token():
    return os.getenv('MLFLOW_TRACKING_TOKEN', None)


def get_mlflow_experiment_path():
    return os.getenv('MLFLOW_EXPERIMENT_PATH', None)

def get_mlflow_experiment_name():
    return os.getenv('MLFLOW_EXPERIMENT_NAME', "Development Default")

def get_use_databricks_tracking_server():
    return os.getenv('USE_DATABRICKS_TRACKING_SERVER', False)


def get_mlflow_gateway_uri():
    return os.getenv('MLFLOW_GATEWAY_URI', "https://deployments.fairo.ai")

def get_mlflow_gateway_chat_route():
    return os.getenv('MLFLOW_GATEWAY_ROUTE', "chat")

def get_mlflow_gateway_embeddings_route():
    return os.getenv('MLFLOW_GATEWAY_ROUTE', "embeddings")
