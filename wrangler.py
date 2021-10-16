# TODO: Handle when the price isn't a value but a text like "CONTACT AGENT"
# TODO: If price is auction or not available in the JSON response at all read the statement of information (if available) as the price HAS to be in there by law.


from dataclasses import asdict, dataclass, field
import datetime
import json
from collections.abc import MutableMapping

@dataclass
class Agent():
    advertiserType: str
    advertiserId: int
    
    def __init__(self, advertiserIdentifiers=None, advertiserType: str = "", advertiserId: int = ""):
        if isinstance(advertiserIdentifiers, dict):
            self.advertiserType = advertiserIdentifiers['advertiserType']
            self.advertiserId = advertiserIdentifiers['advertiserId']
            
        if advertiserType != "" and advertiserId != "":
            self.advertiserType = advertiserType
            self.advertiserId = advertiserId
            
        if (advertiserIdentifiers is None and
            advertiserType == "" and
            advertiserId == ""):
            raise ValueError(f"Not enough information given to create Agent class")
     
@dataclass        
class HouseLocation():
    state: str
    streetNumber: str
    street: str
    suburb: str
    postcode: str
    displayAddress: str
    latitude: float
    longitude: float
    
    def __init__(self, addressParts, geoLocation) -> None:        
        self.state = addressParts['stateAbbreviation'].upper()
        self.streetNumber = addressParts['streetNumber']
        self.street = addressParts['street']
        self.suburb = addressParts['suburb']
        self.postcode = addressParts['postcode']
        self.displayAddress = addressParts['displayAddress']
        self.latitude = geoLocation['latitude']
        self.longitude = geoLocation['longitude']
        
@dataclass        
class HouseDetails():
    bathrooms: int
    bedrooms: int
    carspaces: int
    description: str
    headline: str
    isNewDevelopment: bool
    propertyType: str
    landAreaSqm: int
    
    def __init__(self, raw_listing = None, bathrooms = None, bedrooms = None,
                 carspaces = None, description = None, headline = None, 
                 isNewDevelopment = None, propertyType = None, landAreaSqm = None) -> None:        
        self.bathrooms = bathrooms
        self.bedrooms = bedrooms
        self.carspaces = carspaces
        self.description = description
        self.headline = headline
        self.landAreaSqm = landAreaSqm
        self.isNewDevelopment = isNewDevelopment
        self.propertyType = propertyType
        
        if raw_listing is not None:
            self.bathrooms = raw_listing['bathrooms']
            self.bedrooms = raw_listing['bedrooms']
            self.carspaces = raw_listing['carspaces']
            self.description = raw_listing['description']
            self.headline = raw_listing['headline']
            self.landAreaSqm = raw_listing['landAreaSqm'] if 'landAreaSqm' in raw_listing else None
            self.isNewDevelopment = raw_listing['isNewDevelopment']
            self.propertyType = raw_listing['propertyTypes'][0]
    
@dataclass
class Listing():
    listing_id: int
    created: str
    dateListed: str
    dateUpdated: str
    saleMethod: str
    saleMode: str
    displayPrice: str
    minimumPrice: int 
    maximumPrice: int
    inspectionsByAppointmentOnly: bool
    url: str
    statementOfInformation: str
    location: field(default_factory=HouseLocation)
    house: field(default_factory=HouseDetails)
    agent: field(default_factory=Agent)
    
    def __init__(self, raw_listing = None, listing_id = None, dateListed = None, dateUpdated = None,
                 saleMethod = None, saleMode = None, displayPrice = None, 
                 minimumPrice = None, maximumPrice = None, inspectionsByAppointmentOnly = None,
                 url = None, statementOfInformation = None, location = None,
                 house = None, agent = None) -> None:        
        self.listing_id = listing_id
        self.created = datetime.datetime.utcnow().isoformat()
        self.dateListed = dateListed
        self.dateUpdated = dateUpdated
        self.saleMethod = saleMethod
        self.saleMode = saleMode
        self.displayPrice = displayPrice
        self.minimumPrice = minimumPrice
        self.maximumPrice = maximumPrice
        self.inspectionsByAppointmentOnly = inspectionsByAppointmentOnly
        self.url = url
        self.statementOfInformation = statementOfInformation
        self.location = location
        self.house = house
        self.agent = agent
        
        if raw_listing is not None:
            self.listing_id = raw_listing['id']
            self.dateListed = raw_listing['dateListed']
            self.dateUpdated = raw_listing['dateUpdated']
            self.saleMethod = raw_listing['saleDetails']['saleMethod']
            self.saleMode = raw_listing['saleMode']
            self.displayPrice = raw_listing['priceDetails']['displayPrice']
            self.inspectionsByAppointmentOnly = raw_listing['inspectionDetails']['isByAppointmentOnly']
            self.url = raw_listing['seoUrl']
            self.location = HouseLocation(raw_listing['addressParts'], raw_listing['geoLocation'])
            self.house = HouseDetails(raw_listing)
            self.agent = Agent(raw_listing['advertiserIdentifiers'])
            
            # Handle statementOfInformation
            if 'statementOfInformation' in raw_listing:
                self.statementOfInformation = raw_listing['statementOfInformation']['documentationUrl']
                
            # handle pricing
            if 'price' in raw_listing['priceDetails']:
                self.minimumPrice = self.maximumPrice = raw_listing['priceDetails']['price']
            elif '$' in raw_listing['priceDetails']:
                self.minimumPrice = (raw_listing['priceDetails']['minimumPrice'] 
                                 if 'minimumPrice' in raw_listing['priceDetails']
                                 else get_minimum_price_from_display_price(raw_listing['priceDetails']['displayPrice']))
                self.maximumPrice = (raw_listing['priceDetails']['maximumPrice'] 
                                    if 'maximumPrice' in raw_listing['priceDetails']
                                    else get_maximum_price_from_display_price(raw_listing['priceDetails']['displayPrice']))
                
            
    def __post_init__(self):
        self.minimumPrice = get_minimum_price_from_display_price(self.displayPrice)
    
    def as_no_nested_dicts(self):
        """Returns a dictionary of the listing class that has no nested dictionaries within
        Ensures the class is prepared for tabular data entry
        """
        def _flatten_dict_gen(d, parent_key, sep):
            for k, v in d.items():
                new_key = parent_key + sep + k if parent_key else k
                if isinstance(v, MutableMapping):
                    yield from flatten_dict(v, new_key, sep=sep).items()
                else:
                    yield new_key, v


        def flatten_dict(d: MutableMapping, parent_key: str = '', sep: str = '_'):
            return dict(_flatten_dict_gen(d, parent_key, sep))
 
        return flatten_dict(asdict(self))
        


def get_minimum_price_from_display_price(displayPrice):
    """Get's the minimum value described in a display price. 
    Display price should be in the format "$950,000 - $1,050,000" 

    Args:
        displayPrice ([type]): [description]

    Returns:
        [type]: [description]
    """
    # Clean price
    displayPrice = displayPrice.replace("$", "")
    displayPrice = displayPrice.replace(",", "")
    displayPrice = displayPrice.replace(" ", "")
    
    # Handle a range price eg "$950,000 - $1,050,000"
    return int(displayPrice.split("-")[0])

def get_maximum_price_from_display_price(displayPrice):
    """Get's the maximum value described in a display price. 
    Display price should be in the format "$950,000 - $1,050,000" 

    Args:
        displayPrice ([type]): [description]

    Returns:
        [type]: [description]
    """
    # Clean price
    displayPrice = displayPrice.replace("$", "")
    displayPrice = displayPrice.replace(",", "")
    displayPrice = displayPrice.replace(" ", "")
    
    # Handle a range price eg "$950,000 - $1,050,000"
    return int(displayPrice.split("-")[1])

def get_min_max_price_from_display_price(displayPrice):
    """Get's the maximum value described in a display price. 
    Display price should be in the format "$950,000 - $1,050,000" 

    Args:
        displayPrice (str): The value in the display price

    Returns:
        tuple: first element is minimum and the second is the maximum
    """    
    return (get_minimum_price_from_display_price(displayPrice),
            get_maximum_price_from_display_price(displayPrice))


if __name__ == "__main__":
    with open('examples/raw_listing_3.json', 'r') as infile:
        raw_listing = json.load(infile)
        listing = Listing(raw_listing)
        print(json.dumps(listing.as_no_nested_dicts()))
        
    

