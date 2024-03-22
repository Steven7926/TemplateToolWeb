from pymongo import MongoClient

try:
    # Define your MongoDB connection
    client = MongoClient("mongodb://localhost:27017")
    
    # Choose a database and collection
    db = client["templateTool"]
    collection = db["students"]
    
    # Insert data into the MongoDB collection
    collection.delete_many({})
    
    # Close the MongoDB connection
    client.close()

except Exception as e:
    print(e)