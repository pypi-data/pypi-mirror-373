import os
import requests
import time

from typing import List
from threading import Lock

from wxo_agentic_evaluation.service_provider.provider import Provider
from wxo_agentic_evaluation.utils.utils import is_ibm_cloud_url

AUTH_ENDPOINT_AWS = "https://iam.platform.saas.ibm.com/siusermgr/api/1.0/apikeys/token"
AUTH_ENDPOINT_IBM_CLOUD = "https://iam.cloud.ibm.com/identity/token"
DEFAULT_PARAM = {"min_new_tokens": 1, "decoding_method": "greedy", "max_new_tokens": 400}


class ModelProxyProvider(Provider):
    def __init__(
        self,
        model_id=None,
        api_key=None,
        instance_url=None,
        timeout=300,
        embedding_model_id=None,
        params=None
    ):
        super().__init__()

        instance_url = os.environ.get("WO_INSTANCE", instance_url)
        api_key = os.environ.get("WO_API_KEY", api_key)
        if not instance_url or not api_key:
            raise RuntimeError("instance url and WO apikey must be specified to use WO model proxy")

        self.timeout = timeout
        self.model_id = model_id

        self.embedding_model_id = embedding_model_id

        self.api_key = api_key
        self.is_ibm_cloud = is_ibm_cloud_url(instance_url)
        self.auth_url = AUTH_ENDPOINT_IBM_CLOUD if self.is_ibm_cloud else AUTH_ENDPOINT_AWS
    
        self.instance_url = instance_url
        self.url = self.instance_url + "/ml/v1/text/generation?version=2024-05-01"
        self.embedding_url = self.instance_url + "/ml/v1/text/embeddings"

        self.lock = Lock()
        self.token, self.refresh_time = self.get_token()
        self.params = params if params else DEFAULT_PARAM

    def get_token(self):
        if self.is_ibm_cloud:
            payload = {"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": self.api_key}
            resp = requests.post(self.auth_url, data=payload)
            token_key = "access_token"
        else:
            payload = {"apikey": self.api_key}
            resp = requests.post(self.auth_url, json=payload)
            token_key = "token"
        if resp.status_code == 200:
            json_obj = resp.json()
            token = json_obj[token_key]
            expires_in = json_obj["expires_in"]
            refresh_time = time.time() + int(0.8*expires_in)
            return token, refresh_time

        resp.raise_for_status()

    def refresh_token_if_expires(self):
        if time.time() > self.refresh_time:
            with self.lock:
                if time.time() > self.refresh_time:
                    self.token, self.refresh_time = self.get_token()

    def get_header(self):
        return {"Authorization": f"Bearer {self.token}"}

    def encode(self, sentences: List[str]) -> List[list]:
        if self.embedding_model_id is None:
            raise Exception("embedding model id must be specified for text generation")

        self.refresh_token_if_expires()
        headers = self.get_header()
        payload = {"inputs": sentences, "model_id": self.embedding_model_id, "space_id": "1"}
                   #"timeout": self.timeout}
        resp = requests.post(self.embedding_url, json=payload, headers=headers)

        if resp.status_code == 200:
            json_obj = resp.json()
            return json_obj["generated_text"]

        resp.raise_for_status()

    def query(self, sentence: str) -> str:
        if self.model_id is None:
            raise Exception("model id must be specified for text generation")
        self.refresh_token_if_expires()
        headers = self.get_header()
        payload = {"input": sentence, "model_id": self.model_id, "space_id": "1",
                   "timeout": self.timeout, "parameters": self.params}
        resp = requests.post(self.url, json=payload, headers=headers)
        if resp.status_code == 200:
            return resp.json()["results"][0]["generated_text"]

        resp.raise_for_status()


if __name__ == "__main__":
    provider = ModelProxyProvider(model_id="meta-llama/llama-3-3-70b-instruct", embedding_model_id="ibm/slate-30m-english-rtrvr")
    print(provider.query("ok"))
