from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from model import *



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