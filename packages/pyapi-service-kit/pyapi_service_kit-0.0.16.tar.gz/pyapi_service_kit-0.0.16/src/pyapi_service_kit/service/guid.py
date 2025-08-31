import re


def validate_guid(guid: str) -> str:
    if not guid or not isinstance(guid, str):
        raise ValueError("GUID must be a non-empty string")

    guid = guid.strip()
    if not guid:
        raise ValueError("GUID cannot be empty or whitespace")

    if not re.match(r"^[a-zA-Z0-9_-]+$", guid):
        raise ValueError(
            f"GUID contains invalid characters: {guid}. "
            "Only alphanumeric characters, dots, hyphens, and underscores are allowed."
        )

    return guid
