import os


def values() -> dict[str, str]:
    env = os.getenv("CEREBRIUM_ENV", "prod")

    if env not in ["prod", "dev", "local"]:
        raise ValueError(
            f"Invalid CEREBRIUM_ENV value: {env}. Expected one of 'prod', 'dev', or 'local'."
        )

    # defaults per environment
    api_v1, api_v2, auth_url, client_id = {
        "prod": (
            "https://rest-api.cerebrium.ai",
            "https://rest.cerebrium.ai",
            "https://prod-cerebrium.auth.eu-west-1.amazoncognito.com/oauth2/token",
            "2om0uempl69t4c6fc70ujstsuk",
        ),
        "dev": (
            "https://dev-rest-api.cerebrium.ai",
            "https://dev-rest.cerebrium.ai",
            "https://dev-cerebrium.auth.eu-west-1.amazoncognito.com/oauth2/token",
            "207hg1caksrebuc79pcq1r3269",
        ),
        "local": (
            "http://localhost:4100",
            "http://localhost:4100",
            "https://dev-cerebrium.auth.eu-west-1.amazoncognito.com/oauth2/token",
            "207hg1caksrebuc79pcq1r3269",
        ),
    }[env]

    return {
        "api_url_v1": os.getenv("REST_API_URL", api_v1),
        "api_url_v2": os.getenv("REST_API_URL", api_v2),
        "auth_url": os.getenv("AUTH_URL", auth_url),
        "client_id": os.getenv("CLIENT_ID", client_id),
    }
