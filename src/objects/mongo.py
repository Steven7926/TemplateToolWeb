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
    def __init__(self):
        try:
            self.client = MongoClient(MONGO_CONNECTION_STRING)
            self.db = self.client[MONGO_CLIENT]
            self.collection = self.db[CLIENT_COLLECTION]
        except Exception as e:
            print(f"Error: {str(e)}")

    def insert_all_into_mongodb(self, data) -> dict:
        try:
            students = self.collection.insert_many(data)
            return {"success": True, "ids": students.inserted_ids}
        except Exception as e:
            print(f"Error: {str(e)}")
    
    def delete_all(self) -> dict: 
        try:
            self.collection.delete_many({})
            self.client.close()
            return {"success": True}
        except Exception as e:
            print(f"Error: {str(e)}")
    
    def return_certain_count_no_id(self, limit: int):
        try:
            results = self.collection.find({}).limit(limit)           
            return results
        except Exception as e:
            print(f"Error: {str(e)}")
    
    def return_all(self):
        try:
            results = self.collection.find({}, {'_id': False})           
            return results
        except Exception as e:
            print(f"Error: {str(e)}")
    
    def return_any_like(self, search_text):
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
    
    def update_student(self, values, column_updated, columns):

        try:
            id = values[0]
            student = {'_id': bson.ObjectId(id)}
            new_value = {"$set":  {columns[column_updated-1] : values[column_updated-1]}}
            result = self.collection.update_one(student, new_value)
        except Exception as e:
            print(f"Error: {str(e)}")

    def check_and_delete(self, student_id):
        try:
            student = {'_id': bson.ObjectId(student_id)}
            result = self.collection.find_one_and_delete(student)
            return result
        except Exception as e:
            print(f"Error: {str(e)}")
    
    def check_and_delete_by_fields(self, student_id, student_name, student_class):
        try:
            student = {'id': student_id, "name": student_name, "class": student_class}
            result = self.collection.find_one_and_delete(student)
            return result
        except Exception as e:
            print(f"Error: {str(e)}")

    def find_student(self, student_id):
        try:
            student = {'_id': bson.ObjectId(student_id)}
            result = self.collection.find_one(student)
            return result
        except Exception as e:
            print(f"Error: {str(e)}")
    
    def update_image(self, student_id, image):
        try:
            student = {'_id': bson.ObjectId(student_id)}
            newvalues = { "$set": { 'image': image } }
            result = self.collection.update_one(student, newvalues)
            return result
        except Exception as e:
            print(f"Error: {str(e)}")

    def update_raw_image(self, student_id, image_raw):
        try:
            student = {'_id': bson.ObjectId(student_id)}
            newvalues = { "$set": { 'b64_image': image_raw } }
            result = self.collection.update_one(student, newvalues)
            return result
        except Exception as e:
            print(f"Error: {str(e)}")
    
    def close_client(self):
        try:
            self.client.close()
        except Exception as e:
            print(f"Error: {str(e)}")
    
        

