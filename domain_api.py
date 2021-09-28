import requests
from logger import logger
import json
import os
from dotenv import load_dotenv
load_dotenv()

def get_listings_in_postcode(key: str, postcode: str, page_size: int = 200):
    """Get the current listings by postcode from Domain

    Args:
        key (str): Authentication key
        postcode (str): Postcode you want to search in
        pagesize (int): Max number of listings to return. 200 is the limit given by domain

    Returns:
        list: list of dicts for each listing
    """
    data = {
        "listingType": "Sale",
        "pageSize": page_size,
        "locations":[
            {
                "state":"",
                "region":"",
                "area":"",
                "suburb":"",
                "postCode": postcode,
                "includeSurroundingSuburbs": False
            }
        ]
    }
    url = "https://api.domain.com.au/v1/listings/residential/_search"
    logger.debug(f"Making request to Domain. URL: {url}, Params: {data}")
    res = requests.post(url, headers={"X-Api-Key": key}, data=json.dumps(data))
    return res.json()

if __name__ == "__main__":
    res = get_listings_in_postcode(os.environ.get('DOMAIN_API_KEY'), 3195)
    logger.debug(os.environ.get('DOMAIN_API_KEY'))

    # with open("temp.json", "w") as outfile:
    #     outfile.write(json.dumps(res))