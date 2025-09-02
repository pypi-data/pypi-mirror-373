import requests
from huggingface_hub import configure_http_backend


# https://huggingface.co/docs/datasets/en/cache
# https://github.com/huggingface/huggingface_hub/issues/2343#issuecomment-2173577782

def set_proxy_http_backend(proxy):
    def backend_factory() -> requests.Session:
        session = requests.Session()
        session.proxies = {"http": proxy, "https": proxy}
        return session

    configure_http_backend(backend_factory=backend_factory)
