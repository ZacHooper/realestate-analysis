from configs.domain_key import get_api_key
import os
from dotenv import load_dotenv
load_dotenv()

def test_get_key():
    assert os.getenv('DOMAIN_API_KEY') == get_api_key()