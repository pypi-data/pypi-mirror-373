import platform

import bugsnag
import jwt

from cerebrium.context import get_current_project, get_token_from_config


def init_bugsnag():
    set_bugsnag_user()

    # Get OS & Project information
    os_info = {
        "os_type": platform.system(),
        "os_version": platform.version(),
        "os_release": platform.release(),
    }
    project_id = get_current_project()

    bugsnag.add_metadata_tab("system", os_info)
    bugsnag.add_metadata_tab("project", {"project_id": project_id})


# Function to decode JWT and extract user info
def get_user_info_from_jwt(jwt_token: str):
    try:
        # Decode the JWT token without verification
        decoded_token = jwt.decode(jwt_token, options={"verify_signature": False})
        return decoded_token.get("sub") or decoded_token.get("username")
    except jwt.DecodeError:
        bugsnag.notify(Exception("Invalid JWT token"), severity="warning")
        return None


def set_bugsnag_user():
    jwt_token, _ = get_token_from_config()

    if jwt_token:
        user_id = get_user_info_from_jwt(jwt_token)

        if user_id:

            def before_notify_callback(event):
                event.set_user(id=user_id)

            bugsnag.before_notify(before_notify_callback)
        else:
            bugsnag.notify(
                Exception("Failed to extract user info from JWT"), severity="warning"
            )
    else:
        bugsnag.notify(Exception("JWT token not found in config"), severity="info")
