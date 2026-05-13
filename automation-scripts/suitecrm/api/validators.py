TYPE_MAP = {
    "array": list,
    "number": (int, float),
    "object": dict,
    "string": str,
}


def assert_json_schema(data, schema):
    # 轻量 JSON Schema 校验，覆盖当前 API 冒烟测试需要的 required/type 规则
    expected_type = schema.get("type")
    if expected_type:
        assert isinstance(data, TYPE_MAP[expected_type])

    for key in schema.get("required", []):
        assert key in data

    for key, child_schema in schema.get("properties", {}).items():
        if key in data:
            assert_json_schema(data[key], child_schema)
