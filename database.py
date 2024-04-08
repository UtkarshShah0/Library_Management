import os
from dotenv import load_dotenv

load_dotenv()

from model import Student
from bson import ObjectId

import motor.motor_asyncio

client = motor.motor_asyncio.AsyncIOMotorClient(os.environ.get("MONGO_URI"))
database = client.get_database("Library")
collection = database.get_collection("student")


async def create_student(student):
    document = student
    result = await collection.insert_one(document)
    return result


async def fetch_all_students():
    data = []
    cursor = collection.find({})
    async for document in cursor:
        data.append(Student(**document))
    return data


async def fetch_one(id):
    student_id = ObjectId(id)
    result = await collection.find_one({"_id": student_id})
    return result


async def update_one(id, data):
    student_id = ObjectId(id)
    await collection.update_one({"_id": student_id}, {"$set": data})


async def remove_one(id):
    student_id = ObjectId(id)
    await collection.delete_one({"_id": student_id})