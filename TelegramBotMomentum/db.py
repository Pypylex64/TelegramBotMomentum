import pymongo

client = pymongo.MongoClient('mongodb://heroku_cxl45hw8:letr5ueqjtlqok8tddf6ua59rb@ds251948.mlab.com:51948/heroku_cxl45hw8',
                            retryWrites=False)
                            
users_db = client.get_default_database()["users_db"]
