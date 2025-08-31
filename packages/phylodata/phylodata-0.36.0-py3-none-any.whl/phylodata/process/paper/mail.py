def is_valid_email(email: str) -> bool:
    """Crudely verifies if an email is valid."""
    if "@" not in email:
        return False

    local, domain = email.split("@")
    if not local or not domain:
        return False

    return True
