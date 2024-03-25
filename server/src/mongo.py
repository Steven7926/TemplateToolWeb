from pymongo import MongoClient
import re
import os
from dotenv import load_dotenv
import bson

load_dotenv()
MONGO_CONNECTION_STRING = os.getenv('MONGO_CONNECTION_STRING')
MONGO_CLIENT = os.getenv('MONGO_CLIENT')
CLIENT_COLLECTION = os.getenv('CLIENT_COLLECTION')

# This is the main mongo class where all interactions with the database directly take place. 
# Data is passed here and the functions handle getting and submitting data to the database. 
# It also establishes a connection to the database and closes that connection. 

class Mongo: 
    # Initialize a DB connection
    def __init__(self):
        try:
            self.client = MongoClient(MONGO_CONNECTION_STRING)
            self.db = self.client[MONGO_CLIENT]
            self.collection = self.db[CLIENT_COLLECTION]
        except Exception as e:
            print(f"Error: {str(e)}")

    # Insert excel data as Students into DB
    def insert_all_into_mongodb(self, data: dict) -> dict:
        try:
            students = self.collection.insert_many(data)
            return {"success": True, "ids": students.inserted_ids}
        except Exception as e:
            print(f"Error: {str(e)}")
    
    # Find and Return functions
    def return_certain_count_no_id(self, limit: int) -> dict:
        try:
            results = self.collection.find({}).limit(limit)           
            return results
        except Exception as e:
            print(f"Error: {str(e)}")
    
    def return_all_with_uuid(self) -> dict:
        try:
            results = self.collection.find({})
            return results
        except Exception as e:
            print(f"Error: {str(e)}")
    
    def return_all_no_uuid(self) -> dict:
        try:
            results = self.collection.find({}, {'_id': False})           
            return results
        except Exception as e:
            print(f"Error: {str(e)}")
    
    def return_any_like(self, search_text: str) -> dict:
        try:
            regx = re.compile(search_text, re.IGNORECASE)
            results = self.collection.find(
            {
                '$or': [
                    {'name': regx},  
                    {'class':regx}, 
                    {'teacher':regx},  
                    {'school':regx},  
                    {'location': regx}, 
                    {'year': regx}]
            })
            return results

        except Exception as e:
            print(f"Error: {str(e)}")

    def find_student(self, student_id: str) -> dict:
        try:
            student = {'_id': bson.ObjectId(student_id)}
            result = self.collection.find_one(student)
            return result
        except Exception as e:
            print(f"Error: {str(e)}")
    
    # Update student data functions
    def update_student_one_field(self, id: str, field: str, value: str |  int  | bool) -> dict:
        try:
            student = {'_id': bson.ObjectId(id)}
            new_value = {"$set":  {field : value}}
            result = self.collection.update_one(student, new_value)
            return result
        except Exception as e:
            print(f"Error: {str(e)}")
    
    def update_raw_image(self, student_id: str, image_raw: bytes):
        try:
            student = {'_id': bson.ObjectId(student_id)}
            newvalues = { "$set": { 'b64_image': image_raw } }
            result = self.collection.update_one(student, newvalues)
            return result
        except Exception as e:
            print(f"Error: {str(e)}")
    
    # Deletion functions
    def check_and_delete(self, student_id: str) -> dict:
        try:
            student = {'_id': bson.ObjectId(student_id)}
            result = self.collection.find_one_and_delete(student, {'_id': 0})
            return result
        except Exception as e:
            print(f"Error: {str(e)}")
    
    def check_and_delete_by_fields(self, student_year: int, student_name: str, student_class: str) -> dict:
        try:
            student = {'year': student_year, "name": student_name, "class": student_class}
            result = self.collection.find_one_and_delete(student)
            return result
        except Exception as e:
            print(f"Error: {str(e)}")
    
    def delete_all(self) -> dict: 
        try:
            self.collection.delete_many({})
            self.client.close()
            return {"success": True}
        except Exception as e:
            print(f"Error: {str(e)}")

    #  Close the connection to the DB, should call  after each function call finishes
    def close_client(self):
        try:
            self.client.close()
        except Exception as e:
            print(f"Error: {str(e)}")