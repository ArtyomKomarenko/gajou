from requests import Session
from requests.adapters import HTTPAdapter
from urllib3 import Retry


class RetrySession(Session):
    def __init__(self, retries=3, backoff_factor=0.5, status_forcelist=None):
        super().__init__()
        retry = Retry(total=retries, read=retries, backoff_factor=backoff_factor, status_forcelist=status_forcelist)
        adapter = HTTPAdapter(max_retries=retries)
        self.mount('http://', adapter)
        self.mount('https://', adapter)
