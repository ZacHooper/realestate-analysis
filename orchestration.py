from prefect import task, Flow
from domain_api import get_listings_in_postcode, get_listing
from logger import logger
from mongo import (connect_to_mongo_db, connect_to_domain_raw_collection, 
                   insert_into_collection, connect_to_domain_listings,
                   which_new_listings)
from datetime import datetime
from wrangler import Listing
import os
from dotenv import load_dotenv
load_dotenv()

@task
def get_todays_listings_on_domain(postcode):
    # get new listings
    key = os.environ.get('DOMAIN_API_KEY')
    listings = get_listings_in_postcode(key, postcode)
    if 'detail' in listings:
        if listings['detail'] == "Unable to verify credentials":
            logger.critical(f"Unable to verify domain credentials")
            raise Exception(f"Unable to verify domain credentials")
    logger.info(f"{len(listings)} listings returned from domain API")
    return listings
    
@task
def upload_raw_listings(data):
    # connect to db
    db_user = os.environ.get('MONGO_USERNAME')
    db_password = os.environ.get('MONGO_PASSWORD')
    client = connect_to_mongo_db(db_user, db_password)
    collection = connect_to_domain_raw_collection(client)
    
    # prepare data for upload
    listings_to_insert = {
        'listings': data,
        'created': datetime.utcnow()
    }

    # Insert data
    objectId = insert_into_collection(collection, listings_to_insert)
    if objectId:
        logger.info(f"Successfully inserted today's listings into database")
    
    return objectId

@task
def check_for_new_listings(listings):
    # connect to db
    db_user = os.environ.get('MONGO_USERNAME')
    db_password = os.environ.get('MONGO_PASSWORD')
    client = connect_to_mongo_db(db_user, db_password)
    collection = connect_to_domain_listings(client)
    logger.debug(f"Checking which listings are new. Listings: {listings}")
    new_listings = which_new_listings(collection, listings)
    logger.debug(f"There are {len(new_listings)} new listings from a total {len(listings)} listings currently active")
    return new_listings

@task
def get_listing_ids(listings):
    return [x['listing']['id'] for x in listings]

@task
def get_new_listing_details(listing_id):
    key = os.environ.get('DOMAIN_API_KEY')
    logger.debug(f"Getting listing for listing_id: {listing_id}")
    raw_listing = get_listing(key, listing_id)
    return Listing(raw_listing)

@task
def add_new_listing_to_mongo(listing: Listing):
    # connect to db
    db_user = os.environ.get('MONGO_USERNAME')
    db_password = os.environ.get('MONGO_PASSWORD')
    client = connect_to_mongo_db(db_user, db_password)
    collection = connect_to_domain_listings(client)
    objectId = insert_into_collection(collection, listing.as_no_nested_dicts())
    if objectId:
        logger.info(f"Successfully inserted listing ({listing.listing_id}) into database")
    return objectId
    
    

with Flow("scrape-raw-from-domain") as flow:
    listings = get_todays_listings_on_domain(3195)
    objectId = upload_raw_listings(listings)
    # Check which listings are new
    listing_ids = get_listing_ids(listings)
    new_listing_ids = check_for_new_listings(listing_ids)
    # Get details for new listings
    new_listings = get_new_listing_details.map(new_listing_ids[1:3])
    # Upload new listings to mongo
    new_listing_objectIds = add_new_listing_to_mongo.map(new_listings)
    # Check which listings are sold
    
    # Update listing in mongo
    
flow.run()

# flow.register(project_name="realestate-analysis")