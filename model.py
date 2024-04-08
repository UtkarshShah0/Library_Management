from typing import List, Optional
from pydantic import BaseModel

class Address(BaseModel):
    city: str
    country: str

class Student(BaseModel):
    name: str
    age: int
    address: Address 

class StudentResponse(BaseModel):
    id: Optional[str]


class StudentsResp(BaseModel):
    name: str
    age: int

class StudentData(BaseModel):
    data: List[StudentsResp]


class AddressPatch(BaseModel):
    city: str | None = None
    country: str | None = None

class StudentPatch(BaseModel):
    name: str | None = None
    age: int | None = None 
    address: AddressPatch | None = None
