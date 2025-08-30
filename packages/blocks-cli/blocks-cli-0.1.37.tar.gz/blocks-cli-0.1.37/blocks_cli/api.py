import requests

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from blocks_cli.config.config import config

# Configure retry strategy
retry_strategy = Retry(
    total=5,  # number of retries
    backoff_factor=0.5,  # wait 0.5, 1, 2 seconds between retries
    status_forcelist=[500, 502, 503, 504]  # HTTP status codes to retry on
)

# Create a session with the retry strategy
api_client = requests.Session()
api_client.mount("https://", HTTPAdapter(max_retries=retry_strategy))
api_client.mount("http://", HTTPAdapter(max_retries=retry_strategy))

# Add default headers that will be used for all requests
api_client.headers.update({
    **config.auth.get_auth_headers(),
})