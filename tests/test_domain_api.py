import os
from DomainAnalysis.wrangler import Listing
from DomainAnalysis.domain_api import build_location_parameter, build_query, need_to_run_again
from dotenv import load_dotenv
load_dotenv()

def test_location_parameter_build():
    postcodes = ["3228","3227"]
    expected_result = [{ "postCode": "3228", "includeSurroundingSuburbs": False },
                       { "postCode": "3227", "includeSurroundingSuburbs": False }]  
    
    assert build_location_parameter(postcodes) == expected_result
    
def test_build_query():
    postcodes = ["3228","3227"]
    listing_type = "Sale"
    expected_result = {
        "listingType": "Sale",
        "pageSize": 200,
        "locations": [
            {"postCode": "3228", "includeSurroundingSuburbs": False},
            {"postCode": "3227", "includeSurroundingSuburbs": False}
        ]
    }
    
    assert build_query(postcodes, listing_type) == expected_result
    
def test_need_to_run_again_true():
    x_page_count = 256
    x_page = 1
    page_size = 200
    assert need_to_run_again(x_page_count, x_page, page_size)
    
def test_need_to_run_again_false():
    x_page_count = 256
    x_page = 2
    page_size = 200
    assert ~ need_to_run_again(x_page_count, x_page, page_size)
