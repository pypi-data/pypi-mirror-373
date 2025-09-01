import os


def get_workspace_id():
    return os.environ.get("INTUNED_WORKSPACE_ID")


def get_project_id():
    return os.environ.get("INTUNED_INTEGRATION_ID")


def get_functions_domain():
    return os.environ.get("FUNCTIONS_DOMAIN")


def get_browser_type():
    return os.environ.get("BROWSER_TYPE")
