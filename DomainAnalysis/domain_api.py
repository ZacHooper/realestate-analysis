import requests
from DomainAnalysis.logger import logger
import json
import os
from math import ceil
from dotenv import load_dotenv
load_dotenv()

def build_location_parameter(postcodes):
    locations = [{"postCode": postcode, "includeSurroundingSuburbs": False} for postcode in postcodes]
    return locations

def build_query(postcodes: list, listing_type: str, page_size: int = 200, page_number: int = 1) -> dict:
    """Builds the query to post to the Domain API

    Args:
        postcodes (list): list of postcodes to query
        listing_type (str): What kind of listing: "Sale", "Rent", "Sold"
        page_size (int, optional): How many results to return per request, Max is 200. Defaults to 200.

    Returns:
        dict: dictionary formatted object ready to be used as a request body
    """
    return {
        "listingType": listing_type,
        "pageSize": page_size,
        "pageNumber": page_number,
        "locations": build_location_parameter(postcodes)
    }
    
def need_to_run_again(x_total_count, x_pagination_page_number, page_size):
    """Checks pagination of last request and says whether another request needs to be made. 
    If the `x_pagination_page_number` equals the number of pages then the last request was for the last page
    and the function returns `False`. Otherwise it wasn't the last page and another request is required, 
    resulting in the function returning `True`

    Args:
        x_total_count (int): Total number of listings in search
        x_pagination_page_number (int): Current page of last search
        page_size (int): configuration of search detailing how many listings to return per request.

    Returns:
        bool: True: another page to search on, False: Last page was just searched
    """
    pages = ceil(x_total_count/page_size)
    return False if x_pagination_page_number == pages else True

def get_listings_in_postcode(key: str, postcodes: list, page_size: int = 200, page_number = 1):
    """Get the current listings by postcode from Domain

    Args:
        key (str): Authentication key
        postcode (str): Postcode you want to search in
        pagesize (int): Max number of listings to return. 200 is the limit given by domain

    Returns:
        list: list of dicts for each listing
    """
    data = build_query(postcodes, "Sale", page_size, page_number)
    url = "https://api.domain.com.au/v1/listings/residential/_search"
    do_another_search = True
    listings = []
    
    while do_another_search:
        # Make request
        logger.debug(f"Making request to Domain. URL: {url}, Params: {data}")
        res = requests.post(url, headers={"X-Api-Key": key}, data=json.dumps(data))
        res_json = res.json()
        # If a dict is returned the query likely failed
        if type(res_json) is dict:
            return res_json
        else:
            listings += res_json
        # work out if another query is required
        x_total_count = int(res.headers['X-Total-Count'])
        x_pagination_page_number = int(res.headers['X-Pagination-PageNumber'])
        do_another_search = need_to_run_again(x_total_count, x_pagination_page_number, page_size)
        if do_another_search:
            data['pageNumber'] += 1
        
    return listings

def get_listing(key: str, listing_id: int):
    url = f"https://api.domain.com.au/v1/listings/{listing_id}"
    logger.debug(f"Making request to Domain for specific listing. URL: {url}, listing_id: {listing_id}")
    res = requests.get(url, headers={"X-Api-Key": key})
    return res.json()
    

if __name__ == "__main__":
    # listings = get_listings_in_postcode(os.environ.get("DOMAIN_API_KEY"), ["3228","3227","3226","3230","3231", "3220", "3218", "3195"])
    # # print(len(listings))
    
    listing = get_listing(os.environ.get("DOMAIN_API_KEY"), "2017274398")

    with open("examples/faulty_streetNumber.json", "w") as outfile:
        outfile.write(json.dumps(listing))
    
    