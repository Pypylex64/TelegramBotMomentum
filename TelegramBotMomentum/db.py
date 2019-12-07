import pymongo
from config import MONGO_URI

client = pymongo.MongoClient(MONGO_URI, retryWrites=False)
                            
users_db = client.get_default_database()["users_db"]
