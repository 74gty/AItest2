import requests


class SuiteCrmApiClient:
    def __init__(
        self,
        api_url,
        username=None,
        password=None,
        client_id=None,
        client_secret=None,
        timeout=15,
    ):
        self.api_url = api_url.rstrip("/")
        self.username = username
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret
        self.timeout = timeout
        self.session = requests.Session()

    def authenticate(self):
        # SuiteCRM V8 API 使用 OAuth2 password grant 获取访问令牌
        response = self.session.post(
            f"{self.api_url}/access_token",
            data={
                "grant_type": "password",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "username": self.username,
                "password": self.password,
            },
            timeout=self.timeout,
        )
        if response.ok:
            access_token = response.json().get("access_token")
            if access_token:
                self.session.headers.update({"Authorization": f"Bearer {access_token}"})
        return response

    def authenticate_with_password(self, username, password):
        # 边界条件测试复用同一认证入口，避免在用例里拼请求细节
        return self.session.post(
            f"{self.api_url}/access_token",
            data={
                "grant_type": "password",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "username": username,
                "password": password,
            },
            timeout=self.timeout,
        )

    def get_current_user(self):
        return self.session.get(f"{self.api_url}/V8/current-user", timeout=self.timeout)

    def list_records(self, module_name, params=None):
        return self.session.get(
            f"{self.api_url}/V8/module/{module_name}",
            params=params,
            timeout=self.timeout,
        )

    def get_record(self, module_name, record_id, params=None):
        return self.session.get(
            f"{self.api_url}/V8/module/{module_name}/{record_id}",
            params=params,
            timeout=self.timeout,
        )

    def create_record(self, module_name, attributes):
        return self.session.post(
            f"{self.api_url}/V8/module",
            json={"data": {"type": module_name, "attributes": attributes}},
            timeout=self.timeout,
        )

    def update_record(self, module_name, record_id, attributes):
        return self.session.patch(
            f"{self.api_url}/V8/module",
            json={"data": {"type": module_name, "id": record_id, "attributes": attributes}},
            timeout=self.timeout,
        )

    def delete_record(self, module_name, record_id):
        return self.session.delete(
            f"{self.api_url}/V8/module/{module_name}/{record_id}",
            timeout=self.timeout,
        )
