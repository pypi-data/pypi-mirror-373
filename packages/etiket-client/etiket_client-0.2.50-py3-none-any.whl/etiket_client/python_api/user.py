from etiket_client.settings.user_settings import user_settings

def get_current_user():
    if user_settings.user_sub is None:
        raise ValueError("No user is logged in")
    return user_settings.user_sub
