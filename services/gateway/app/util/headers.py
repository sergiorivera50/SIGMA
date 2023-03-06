def isAuthType(header, auth_type="Basic"):
    return header.startswith(f"{auth_type} ")
