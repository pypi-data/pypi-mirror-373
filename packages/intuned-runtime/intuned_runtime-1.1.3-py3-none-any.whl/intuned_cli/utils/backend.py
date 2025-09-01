import os


def get_base_url():
    return os.environ.get("INTUNED_API_DOMAIN", "https://app.intuned.io")
