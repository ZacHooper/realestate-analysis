from prefect import task, Flow, unmapped, Parameter
from prefect.storage.github import GitHub
from prefect.run_configs.docker import DockerRun
from prefect.tasks.secrets import PrefectSecret
from DomainAnalysis.domain_api import get_listings_in_postcode, get_listing
from DomainAnalysis.logger import logger
from DomainAnalysis.mongo import (connect_to_mongo_db, connect_to_domain_raw_collection, 
                   insert_into_collection, connect_to_domain_listings,
                   which_new_listings)
from datetime import datetime
from DomainAnalysis.wrangler import Listing
import os
from dotenv import load_dotenv
load_dotenv()

@task
def get_todays_listings_on_domain(domain_key, postcode):
    # get new listings
    listings = get_listings_in_postcode(domain_key, postcode)
    if type(listings) is dict:
        if listings['detail'] == "Unable to verify credentials":
            logger.critical(f"Unable to verify domain credentials")
            raise Exception(f"Unable to verify domain credentials")
    logger.info(f"{len(listings)} listings returned from domain API")
    return listings
    
@task
def upload_raw_listings(client, data):    
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
def check_for_new_listings(client, listings):
    # connect to db
    collection = connect_to_domain_listings(client)
    logger.debug(f"Checking which listings are new. Listings: {listings}")
    new_listings = which_new_listings(collection, listings)
    logger.debug(f"There are {len(new_listings)} new listings from a total {len(listings)} listings currently active")
    return new_listings

@task
def get_listing_ids(listings):
    return [x['listing']['id'] for x in listings]

@task
def get_new_listing_details(domain_key, listing_id):
    logger.debug(f"Getting listing for listing_id: {listing_id}")
    raw_listing = get_listing(domain_key, listing_id)
    try:
        listing = Listing(raw_listing)
        return listing
    except Exception as e:
        logger.critical(f"Unable to create listing class due to: {e}")
        raise ValueError(f"Unable to create listing class due to: {e}")

@task
def add_new_listing_to_mongo(client, listing: Listing):
    # connect to db
    collection = connect_to_domain_listings(client)
    # TODO: Add handle if listing is "NoneType"
    objectId = insert_into_collection(collection, listing.as_no_nested_dicts())
    if objectId:
        logger.info(f"Successfully inserted listing ({listing.listing_id}) into database")
    return objectId

@task
def connect_to_mongo(db_user, db_password):
    """Connects to domain analysis mongo db

    Args:
        db_user (str): username
        db_password (str): MongoDB password

    Returns:
        client: MongoDB database
    """
    return connect_to_mongo_db(db_user, db_password)
    
    

with Flow("scrape-raw-from-domain") as flow:
    # Creds
    db_user = PrefectSecret('MONGO_USERNAME')
    db_password = PrefectSecret('MONGO_PASSWORD')
    domain_key = PrefectSecret('DOMAIN_API_KEY')
    
    # Params
    postcodes = Parameter('postcodes', default=["3228","3227","3226","3230","3231", "3220", "3218", "3195"])
    
    # Connect to Mongo
    client = connect_to_mongo(db_user, db_password)
    
    # 3228: Torquay
    # 3227: Barwon Heads
    # 3226: Ocean Grove
    # 3230: Angelsea
    # 3231: Airey's
    # 3220: Geelong City / Newtown
    # 3218: Geelong West
    
    listings = get_todays_listings_on_domain(domain_key, postcodes)
    objectId = upload_raw_listings(client, listings)
    # Check which listings are new
    listing_ids = get_listing_ids(listings)
    new_listing_ids = check_for_new_listings(client, listing_ids)
    # Get details for new listings
    new_listings = get_new_listing_details.map(unmapped(domain_key), new_listing_ids)
    # Upload new listings to mongo
    new_listing_objectIds = add_new_listing_to_mongo.map(unmapped(client), new_listings)
    # Check which listings are sold
    
    # Update listing in mongo
    
flow.run()

flow.storage = GitHub(repo = "ZacHooper/realestate-analysis", path="/flows/orchestration.py")
flow.run_config = DockerRun(image = "zhooper/domain-analysis")
# flow.register(project_name="realestate-analysis", labels=["testing"])