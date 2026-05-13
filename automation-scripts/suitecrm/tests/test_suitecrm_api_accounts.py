from uuid import uuid4

import pytest

from suitecrm.api.schemas import JSON_API_LIST_SCHEMA, JSON_API_SINGLE_SCHEMA, OAUTH_TOKEN_SCHEMA
from suitecrm.api.validators import assert_json_schema


pytestmark = [pytest.mark.suitecrm, pytest.mark.api]


def test_suitecrm_api_login_and_list_accounts(suitecrm_api_client):
    token_response = suitecrm_api_client.authenticate()
    assert token_response.status_code == 200
    assert_json_schema(token_response.json(), OAUTH_TOKEN_SCHEMA)

    accounts_response = suitecrm_api_client.list_records(
        "Accounts",
        params={"page[size]": 5, "fields[Accounts]": "name,account_type"},
    )
    assert accounts_response.status_code == 200
    assert_json_schema(accounts_response.json(), JSON_API_LIST_SCHEMA)


def test_suitecrm_api_account_crud(suitecrm_api_client):
    token_response = suitecrm_api_client.authenticate()
    assert token_response.status_code == 200

    account_name = f"EUTL API Account {uuid4().hex[:8]}"
    created_id = None

    try:
        create_response = suitecrm_api_client.create_record(
            "Accounts",
            {"name": account_name, "account_type": "Customer"},
        )
        assert create_response.status_code in (200, 201)
        assert_json_schema(create_response.json(), JSON_API_SINGLE_SCHEMA)

        created_id = create_response.json()["data"]["id"]
        get_response = suitecrm_api_client.get_record("Accounts", created_id)
        assert get_response.status_code == 200
        assert get_response.json()["data"]["attributes"]["name"] == account_name

        updated_name = f"{account_name} Updated"
        update_response = suitecrm_api_client.update_record(
            "Accounts",
            created_id,
            {"name": updated_name},
        )
        assert update_response.status_code == 200

        verify_response = suitecrm_api_client.get_record("Accounts", created_id)
        assert verify_response.status_code == 200
        assert verify_response.json()["data"]["attributes"]["name"] == updated_name
    finally:
        if created_id:
            delete_response = suitecrm_api_client.delete_record("Accounts", created_id)
            assert delete_response.status_code in (200, 204)


def test_suitecrm_api_rejects_wrong_password(suitecrm_api_client):
    response = suitecrm_api_client.authenticate_with_password("bad-user", "bad-password")
    assert response.status_code in (400, 401)
