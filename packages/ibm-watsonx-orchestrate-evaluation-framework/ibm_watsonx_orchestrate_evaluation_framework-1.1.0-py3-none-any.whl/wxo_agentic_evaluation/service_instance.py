import logging
import yaml
import os
import requests
from wxo_agentic_evaluation.utils.utils import is_saas_url, is_ibm_cloud_url

logger = logging.getLogger(__name__)

USER = {"username": "wxo.archer@ibm.com", "password": "watsonx"}


class ServiceInstance:
    def __init__(
        self, service_url, tenant_name, is_saas: bool = None, is_ibm_cloud: bool = None
    ) -> None:
        self.service_url = service_url
        self.tenant_name = tenant_name
        STAGING_AUTH_ENDPOINT = (
            "https://iam.platform.test.saas.ibm.com/siusermgr/api/1.0/apikeys/token"
        )
        PROD_AUTH_ENDPOINT = (
            "https://iam.platform.saas.ibm.com/siusermgr/api/1.0/apikeys/token"
        )
        PROD_AUTH_ENDPOINT_IBMCLOUD = "https://iam.cloud.ibm.com/identity/token"

        self.is_saas = is_saas_url(service_url) if is_saas is None else is_saas
        self.is_ibm_cloud = (
            is_ibm_cloud_url(service_url) if is_ibm_cloud is None else is_ibm_cloud
        )

        if self.is_saas:
            if self.is_ibm_cloud:
                self.auth_endpoint = PROD_AUTH_ENDPOINT_IBMCLOUD
            else:
                self.auth_endpoint = (
                    STAGING_AUTH_ENDPOINT
                    if "staging" in service_url
                    else PROD_AUTH_ENDPOINT
                )
            self.tenant_url = None  # Not used in SaaS
            self.tenant_auth_endpoint = None
        else:
            self.auth_endpoint = f"{service_url}/api/v1/auth/token"
            self.tenant_url = f"{service_url}/tenants"
            self.tenant_auth_endpoint = "{}/api/v1/auth/token?tenant_id={}"

        self.global_token = self.get_user_token()

    def get_user_token(self):
        try:
            if self.is_saas:
                apikey = os.environ.get("WO_API_KEY")
                if not apikey:
                    raise RuntimeError(
                        "WO_API_KEY not set in environment for SaaS mode"
                    )
                if self.is_ibm_cloud:
                    data = {
                        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                        "apikey": apikey,
                    }
                    response = requests.post(self.auth_endpoint, data=data)
                    token_key = "access_token"
                else:
                    headers = {
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                    }
                    payload = {"apikey": apikey}
                    response = requests.post(
                        self.auth_endpoint, headers=headers, json=payload
                    )
                    token_key = "token"
            else:
                response = requests.post(self.auth_endpoint, data=USER)
                token_key = "access_token"

            return response.json()[token_key]

        except KeyError as e:
            print(
                f"[ERROR] Missing key '{e}' in response. SaaS mode: {self.is_saas}. Full response: {response.text}"
            )
            raise
        except requests.RequestException as e:
            print(f"[ERROR] Request failed: {e}")
            raise

    def _get_tenant_token(self, tenant_id: str):
        resp = requests.post(
            self.tenant_auth_endpoint.format(self.service_url, tenant_id), data=USER
        )
        if resp.status_code == 200:
            return resp.json()["access_token"]
        else:
            resp.raise_for_status()

    def get_default_tenant(self, apikey):
        headers = {
            "Authorization": f"Bearer {apikey}",
            "Content-Type": "application/json",
        }
        resp = requests.get(self.tenant_url, headers=headers)
        if resp.status_code == 200:
            tenant_config = resp.json()
            for tenant in tenant_config:
                if tenant["name"] == self.tenant_name:
                    return tenant
            return {}
        else:
            resp.raise_for_status()

    def create_eval_tenant(self, apikey):
        headers = {
            "Authorization": f"Bearer {apikey}",
            "Content-Type": "application/json",
        }

        tenant_config = {
            "name": self.tenant_name,
            "title": "WatsonX Orchestrate Development",
            "tags": ["test"],
        }

        resp = requests.post(self.tenant_url, headers=headers, json=tenant_config)
        if resp.status_code == 201:
            return True
        else:
            resp.raise_for_status()

    def create_tenant_if_not_exist(self) -> str:
        if self.is_saas:
            logger.info(
                "SaaS mode: running against Remote Service and skipping tenant creation"
            )
            return None

        user_auth_token = self.global_token
        default_tenant = self.get_default_tenant(user_auth_token)

        if not default_tenant:
            logger.info("no local tenant found. A default tenant is created")
            self.create_eval_tenant(user_auth_token)
            default_tenant = self.get_default_tenant(user_auth_token)
        else:
            logger.info("local tenant found")

        return default_tenant["id"]


def tenant_setup(service_url: str, tenant_name: str):
    # service_instance = ServiceInstance(
    #     service_url=service_url,
    #     tenant_name=tenant_name
    # )
    # tenant_id = service_instance.create_tenant_if_not_exist()
    # if service_instance.is_saas:
    #     tenant_token = service_instance.global_token
    # else:
    #     tenant_token = service_instance._get_tenant_token(tenant_id)

    auth_config_path = f"{os.path.expanduser('~')}/.cache/orchestrate/credentials.yaml"
    env_config_path = f"{os.path.expanduser('~')}/.config/orchestrate/config.yaml"

    # TO-DO: update SDK and use SDK to manage this
    with open(auth_config_path, "r") as f:
        auth_config = yaml.safe_load(f)
    # auth_config["auth"][tenant_name] = {"wxo_mcsp_token": tenant_token}

    with open(env_config_path, "r") as f:
        env_config = yaml.safe_load(f)
    env_config["environments"][tenant_name] = {"wxo_url": service_url}
    env_config["context"]["active_environment"] = tenant_name

    with open(auth_config_path, "w") as f:
        yaml.dump(auth_config, f)
    with open(env_config_path, "w") as f:
        yaml.dump(env_config, f)
    return auth_config["auth"][tenant_name]["wxo_mcsp_token"]
