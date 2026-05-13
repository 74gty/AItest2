JSON_API_SINGLE_SCHEMA = {
    "type": "object",
    "required": ["data"],
    "properties": {
        "data": {"type": "object", "required": ["type", "id", "attributes"]},
    },
}

JSON_API_LIST_SCHEMA = {
    "type": "object",
    "required": ["data"],
    "properties": {
        "data": {"type": "array"},
    },
}

OAUTH_TOKEN_SCHEMA = {
    "type": "object",
    "required": ["access_token", "token_type", "expires_in"],
    "properties": {
        "access_token": {"type": "string"},
        "token_type": {"type": "string"},
        "expires_in": {"type": "number"},
    },
}
