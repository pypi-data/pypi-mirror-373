def requiredScopesForView(this_view):
    return {
        "GET": [[this_view + ":read"]],
        "OPTIONS": [[this_view + ":read"]],
        "HEAD": [[this_view + ":read"]],
        "POST": [[this_view + ":create"]],
        "PUT": [[this_view + ":update"]],
        "PATCH": [[this_view + ":update"]],
        "DELETE": [[this_view + ":delete"]],
    }
