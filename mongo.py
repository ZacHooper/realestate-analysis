from pymongo import MongoClient
from logger import logger
import os
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

def insert_into_collection(coll, data):
    """Inserts a JSON object into a MongoDB collection

    Args:
        coll (Collection): Mongo Collection in Database
        data (dict): dictionary (or JSON object) to insert into Database

    Returns:
        ObjectId: Unique ObjectId set for the document
    """
    logger.debug(f"Inserting into collection ({coll.name}): {data}")
    try:
        object_id = coll.insert_one(data).inserted_id
        logger.debug(f"Successfully inserted data into collection. Object ID: {object_id}")
    except Exception as e:
        logger.critical(f"Unable to insert data into DB because: {e} \n-- ARGUMENTS USED -- \nCollection: {coll.name}, \ndata: {data}")
        raise Exception(f"Unable to insert data into DB because: {e} \n-- ARGUMENTS USED -- \nCollection: {coll.name}, \ndata: {data}")

    return object_id

if __name__ == "__main__":
    client = connect_to_mongo_db()
    domain_coll = connect_to_domain_raw_collection(client)
