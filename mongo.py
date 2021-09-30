from pymongo import MongoClient, DESCENDING
from bson.objectid import ObjectId
from logger import logger
import os
import json
from dotenv import load_dotenv
load_dotenv()

def connect_to_mongo_db(db_user = "", db_password = ""):
    if db_user == "" and db_password == "":
        db_user = os.environ.get('MONGO_USERNAME')
        db_password = os.environ.get('MONGO_PASSWORD')
    
    connection_string = f"mongodb+srv://{db_user}:{db_password}@raw-requests.gz569.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
    try:
        logger.debug(f"Attempting to connect to MongoDB")
        client = MongoClient(connection_string)
        logger.debug(f"Successfully connected")
    except Exception as e:
        logger.critical(f"Unable to connect to db because {e}")
        raise Exception(f"Unable to connect to db because {e}")
    return client

def connect_to_domain_raw_collection(client):
    return client['raw-requests'].domain

def connect_to_domain_listings(client):
    return client['raw-requests'].listings

def insert_into_collection(coll, data):
    """Inserts a JSON object into a MongoDB collection

    Args:
        coll (Collection): Mongo Collection in Database
        data (dict): dictionary (or JSON object) to insert into Database

    Returns:
        ObjectId: Unique ObjectId set for the document
    """
    logger.debug(f"Inserting into collection ({coll.name}): {data.keys()}")
    try:
        object_id = coll.insert_one(data).inserted_id
        logger.debug(f"Successfully inserted data into collection. Object ID: {object_id}")
    except Exception as e:
        logger.critical(f"Unable to insert data into DB because: {e} \n-- ARGUMENTS USED -- \nCollection: {coll.name}, \ndata: {data}")
        raise Exception(f"Unable to insert data into DB because: {e} \n-- ARGUMENTS USED -- \nCollection: {coll.name}, \ndata: {data}")

    return object_id

def read_recent_record(coll, objectId = None):
    """Get's the last inserted document into the collection. 
    If specific objectId provided will instead get that exact document.

    Args:
        coll (Collection): Pymongo collection
        objectId (ObjectId, optional): ObjectId of the specific document to get. Defaults to None.

    Returns:
        dict: Document from MongoDB Collection
    """
    if objectId is not None:
        logger.debug(f"Finding document with ObjectId: {objectId}")
        data = coll.find_one({"_id": objectId})
    else:
        data = coll.find_one(sort=[('_id', DESCENDING)])
    
    logger.debug(f"Document found. Num of listings in Document: {len(data['listings'])}")
    return data

def which_new_listings(coll, listing_ids, return_existing = False):
    """Check Mongo DB for wich listing IDs don't currently exist in the database

    Args:
        coll (Collection): MongoDB collection
        listing_ids (list): List of listing_ids
        return_existing (bool, optional): Option to return the existings IDs rather than new. Defaults to False.

    Returns:
        list: List of listing_ids
    """
    query = {"listing_id":{"$in": listing_ids}}
    project = {"listing_id":1}
    # Create a list of the listing ids found in the database
    existing_listing_ids = [x['listing_id'] for x in coll.find(query, project)]
    # Return the existing ids if requested
    if return_existing:
        return existing_listing_ids
    # Only return the ids in listing ids but NOT in existing ids
    return [x for x in listing_ids if x not in existing_listing_ids]

if __name__ == "__main__":
    client = connect_to_mongo_db()
    domain_coll = connect_to_domain_raw_collection(client)
    listing_coll = connect_to_domain_listings(client)
    listings = [2017273091, 2017272108, 2017278297, 12345, 67890, 9876, 54321]
    new_listings = which_new_listings(listing_coll, listings)
    print(new_listings)
