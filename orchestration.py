from prefect import task, Flow
from domain_api import get_listings_in_postcode
from logger import logger
from mongo import (connect_to_mongo_db, connect_to_domain_raw_collection, 
                   insert_into_collection, connect_to_domain_listings)
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()

@task
def get_todays_listings_on_domain():
    # get new listings
    key = os.environ.get('DOMAIN_API_KEY')
    listings = get_listings_in_postcode(key, 3195)
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
def check_for_new_listings():
    # connect to db
    db_user = os.environ.get('MONGO_USERNAME')
    db_password = os.environ.get('MONGO_PASSWORD')
    client = connect_to_mongo_db(db_user, db_password)
    collection = connect_to_domain_listings(client)
    

with Flow("scrape-raw-from-domain") as flow:
    listings = get_todays_listings_on_domain()
    objectId = upload_raw_listings(listings)
    # Check which listings are new
    
    # Get details for new listings
    
    # Upload new listings to mongo
    
    # Check which listings are sold
    
    # Update listing in mongo

flow.register(project_name="realestate-analysis")