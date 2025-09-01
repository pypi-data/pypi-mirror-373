__all__ = ["access_timeout", "already_authenticated", "inactive_disallowed", "unauthorized", "forbidden",
           "account_blocked", "invalid_credentials", "csrf_invalid", "need_password_confirm"]

access_timeout = {
    419: "Access token expired"
}

already_authenticated = {
    403: "User already authenticated"
}

inactive_disallowed = {
    403: "Inactive user disallowed"
}

unauthorized = {
    401: "Unauthorized"
}

forbidden = {
    403: "Forbidden"
}

account_blocked = {
    403: "Block reason"
}

invalid_credentials = {
    401: "Invalid credentials"
}

csrf_invalid = {
    403: "CSRF token invalid"
}

need_password_confirm = {
    403: "Need password confirmation"
}
