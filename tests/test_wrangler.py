import json
import datetime
import pytest
from DomainAnalysis.wrangler import *

@pytest.fixture
def raw_listing():
    with open('examples/raw_listing.json', 'r') as infile:
        l = json.load(infile)
    return l

@pytest.fixture
def listing(raw_listing):
    return Listing(raw_listing)

@pytest.fixture
def no_insp_listing():
    with open('examples/faulty_inspectionDetails.json', 'r') as infile:
        l = json.load(infile)
        return l
    
@pytest.fixture
def no_street_number():
    with open('examples/faulty_streetNumber.json', 'r') as infile:
        l = json.load(infile)
    return l

def test_get_minimum_price_from_display_price(raw_listing):
    displayPrice1 = "$950,000 - $1,050,000"
    displayPrice2 = "950,000 - 1,050,000"
    displayPrice3 = "950,000-1,050,000"
    displayPrice4 = "950 ,000-1,050,000"
    displayPrice5 = "950,000 1,050,000" # Not currently handled
    displayPrice6 = "$1,300,000 to $1,400,000"
    assert get_minimum_price_from_display_price(displayPrice1) == 950000
    assert get_minimum_price_from_display_price(displayPrice2) == 950000
    assert get_minimum_price_from_display_price(displayPrice3) == 950000
    assert get_minimum_price_from_display_price(displayPrice4) == 950000
    # assert get_minimum_price_from_display_price(displayPrice5) == 950000
    assert get_minimum_price_from_display_price(displayPrice6) == 1300000
    
def test_get_maximum_price_from_display_price(raw_listing):
    displayPrice1 = "$950,000 - $1,050,000"
    displayPrice2 = "950,000 - 1,050,000"
    displayPrice3 = "950,000-1,050,000"
    displayPrice4 = "950 ,000-1,050,000"
    displayPrice5 = "950,000 1,050,000" # Not currently handled
    displayPrice6 = "$1,300,000 to $1,400,000"
    assert get_maximum_price_from_display_price(displayPrice1) == 1050000
    assert get_maximum_price_from_display_price(displayPrice2) == 1050000
    assert get_maximum_price_from_display_price(displayPrice3) == 1050000
    assert get_maximum_price_from_display_price(displayPrice4) == 1050000
    # assert get_minimum_price_from_display_price(displayPrice5) == 950000
    assert get_maximum_price_from_display_price(displayPrice6) == 1400000
    
def test_get_min_max_price_from_display_price(raw_listing):
    displayPrice1 = "$950,000 - $1,050,000"
    displayPrice2 = "950,000 - 1,050,000"
    displayPrice3 = "950,000-1,050,000"
    displayPrice4 = "950 ,000-1,050,000"
    displayPrice5 = "950,000 1,050,000" # Not currently handled
    assert get_min_max_price_from_display_price(displayPrice1) == (950000, 1050000)
    assert get_min_max_price_from_display_price(displayPrice2) == (950000, 1050000)
    assert get_min_max_price_from_display_price(displayPrice3) == (950000, 1050000)
    assert get_min_max_price_from_display_price(displayPrice4) == (950000, 1050000)
    # assert get_minimum_price_from_display_price(displayPrice5) == 950000
    
def test_get_min_max_price_from_display_price_unpack(raw_listing):
    displayPrice1 = "$950,000 - $1,050,000"
    min_price, max_price = get_min_max_price_from_display_price(displayPrice1)
    assert min_price == 950000
    assert max_price == 1050000
    
    
def test_agent_class_dict(raw_listing):
    a = Agent(raw_listing['advertiserIdentifiers'])
    assert isinstance(a, Agent)
    assert a.advertiserType == "agency"
    assert a.advertiserId == 5600
    
def test_agent_class_args():
    a = Agent(advertiserType="agency", advertiserId=5600)
    assert isinstance(a, Agent)
    assert a.advertiserType == "agency"
    assert a.advertiserId == 5600
    
def test_agent_class_dict_n_args(raw_listing):
    a = Agent(raw_listing['advertiserIdentifiers'], advertiserType="agencies", advertiserId=56002)
    assert isinstance(a, Agent)
    assert a.advertiserType == "agencies"
    assert a.advertiserId == 56002
    
def test_agent_class_raise_error():
    with pytest.raises(ValueError) as e_info:
        a = Agent()
        
def test_houseLocation_class_dict(raw_listing):
    hl = HouseLocation(raw_listing['addressParts'], raw_listing['geoLocation'])
    assert isinstance(hl, HouseLocation)
    assert hl.state == "VIC"
    assert hl.streetNumber == "12C"
    assert hl.street == "Melrose Street"
    assert hl.suburb == "Mordialloc"
    assert hl.postcode == "3195"
    assert hl.displayAddress == "12C Melrose Street, Mordialloc VIC 3195"
    assert hl.latitude == -37.999497
    assert hl.longitude == 145.086221
    
def test_houseLocation_class_args():
    with pytest.raises(TypeError) as e_info:        
        hl = HouseLocation(raw_listing['addressParts'])
        
def test_house_details_class_dict(raw_listing):
    hd = HouseDetails(raw_listing)
    assert isinstance(hd, HouseDetails)
    assert hd.bathrooms == 2
    assert hd.bedrooms == 3
    assert hd.carspaces == 2
    assert hd.description == "OPEN FOR PRIVATE INSPECTION SAT 2ND OCTOBER - 11:00AM - 12:30PM\r\n\r\nCall Today to Pre-Book your Inspection! Limited Spaces Available!!\r\n\r\nThis property is available for private one-on-one inspections. \r\nIt is a requirement for buyers to book an appointment before attending any inspection \r\nDon't miss yours contact  Jonathon on 0476 241 706 or email Jonathon.hannan@raywhite.com to make a booking.\r\n\r\nSet at the rear of an attractive allotment shared with only two other residences, this exceptional modern unit brings size and style together to create a superlative single level combination close to shopping options, Bradshaw Park, the beach and central to both Parkdale and Mordialloc train stations. Ducted heating throughout, timber floors and faultless presentation have an instant impact throughout spaces that include a generous living/dining area, a sparkling stainless steel equipped kitchen and a substantial study zone. The Master bedroom has its own ensuite, while the two other desirable bedrooms share a modern central bathroom. The presence of private decking enhances appealing outdoor surroundings, further complemented by the convenience of a secure double garage. A great way to live, a wise way to invest."
    assert hd.headline == "Enjoy, Invest, Best Of Both!"
    assert hd.landAreaSqm == None
    assert hd.isNewDevelopment == False
    assert hd.propertyType == "house"
    
def test_listing_class_dict(raw_listing):
    l = Listing(raw_listing)
    assert isinstance(l, Listing)
    assert l.listing_id == 2017278297
    assert l.dateListed == "2021-09-24T06:43:18Z"
    assert l.dateUpdated == "2021-09-27T22:29:18.3Z"
    assert l.saleMethod == "auction"
    assert l.saleMode == "buy"
    assert l.displayPrice == "$950,000 - $1,050,000"
    assert l.minimumPrice == 950000
    assert l.maximumPrice == 1050000
    assert l.inspectionsByAppointmentOnly == False
    assert l.url == "https://www.domain.com.au/12c-melrose-street-mordialloc-vic-3195-2017278297"
    assert l.statementOfInformation == "https://s3-ap-southeast-2.amazonaws.com/p-statement-of-information/comaust%235600%23l14795446%23"
    assert isinstance(l.location, HouseLocation)
    assert isinstance(l.house, HouseDetails)
    assert isinstance(l.agent, Agent)
    
def test_lising_asdict(listing):
    # Check to see that not items are nested objects
    assert all([not isinstance(y[1],dict) for y in  listing.as_no_nested_dicts().items()])
    
def test_listing_with_no_inspectionDetails(no_insp_listing):
    l = Listing(no_insp_listing)
    assert isinstance(l, Listing)
    assert l.inspectionsByAppointmentOnly == None
    
def test_listing_is_suburb_address(no_insp_listing: Listing):
    l = Listing(no_insp_listing)
    assert isinstance(l, Listing)
    assert l.location.streetNumber == None
    assert l.location.postcode == "3195"
    
def test_no_geolocation(no_insp_listing: Listing):
    l = Listing(no_insp_listing)
    assert l.location.latitude == None
    
def test_if_no_street_number_present(no_street_number):
    l = Listing(no_street_number)
    assert l.location.streetNumber == None
    
def test_only_one_price_in_display_price(no_street_number):
    l = Listing(no_street_number)
    assert l.minimumPrice == 600000
    
