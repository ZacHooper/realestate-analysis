from domain_api import get_listings_in_postcode
from logger import logger
from mongo import connect_to_mongo_db, connect_to_domain_raw_collection, insert_into_collection
from configs.db import get_mongo_details
from configs.domain_key import get_api_key
from datetime import datetime

if __name__ == "__main__":
    # connect to db
    db_user, db_password = get_mongo_details()
    client = connect_to_mongo_db(db_user, db_password)
    collection = connect_to_domain_raw_collection(client)

    # get new listings
    key = get_api_key()
    listings = get_listings_in_postcode(key, 3195)
    logger.info(f"{len(listings)} listings returned from domain API")

    # prepare data for upload
    listings_to_insert = {
        'listings': listings,
        'created': datetime.utcnow()
    }

    # Insert data
    objectId = insert_into_collection(collection, listings_to_insert)
    if objectId:
        logger.info(f"Successfully inserted today's listings into database")
