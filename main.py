from fastapi import FastAPI, Query, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from model import *

from aioredis import Redis 
from datetime import datetime



# App initialisation
app = FastAPI()


from database import (
    create_student,
    fetch_all_students, 
    fetch_one, 
    update_one,
    remove_one
)


# CORS
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],

)


# Redis Connection
async def get_redis():
    return await Redis.from_url("redis://localhost")


# Rate limiter 
async def rate_limiter(request: Request, redis: Redis):
    user_id = request.headers.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="No User ID")
    
    today = datetime.now().date().isoformat()

    key = f"rate_limiter:{user_id}:{today}"
    count = await redis.get(key)
    if count is None:
        await redis.setex(key, 86400, 1)
    else:
        count = int(count)
        if count >= 5:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        await redis.incr(key)


# Middleware

@app.middleware("http")
async def check_rate_limit(request: Request, call_next):
    redis = await get_redis()
    try:
        await rate_limiter(request, redis)
    except HTTPException as e:
        return Response(content = e.detail, status_code=e.status_code)
    else:
        response = await call_next(request)
        return response



# Endpoints

@app.post("/students", response_model=StudentResponse, status_code=201)
async def create_students(student:Student):
    response = await create_student(student.model_dump())
    inserted_id = response.inserted_id
    return {"id": str(inserted_id)}


@app.get("/students", response_model=StudentData, status_code=200)
async def list_students(country: Optional[str] = Query(None), age: Optional[int] = Query(None)):
    response = await fetch_all_students()
    
    if country:
        response = [student for student in response if student.address.country == country]
    
    if age:
        response = [student for student in response if student.age >= age]
    
    result = [{"name": student.name, "age": student.age} for student in response]

    return {"data": result}


@app.get("/students/{id}", response_model=Student, status_code=200)
async def fetch_student(id: str):
    data = await fetch_one(id)
    if data:
        result = Student(**data)
        return result
    else:
        raise HTTPException(status_code=404, detail="Student not found")



@app.patch("/students/{id}", response_model=None, status_code=204)
async def update_student(id: str, student_data: StudentPatch):
    update_data = student_data.model_dump(exclude_unset = True)
    print(update_data) 
    await update_one(id, update_data)
    return

@app.delete("/students/{id}", response_model=dict, status_code=200)
async def delete_student(id: str):
    await remove_one(id)
    return {}
