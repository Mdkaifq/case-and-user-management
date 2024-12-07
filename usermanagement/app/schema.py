import strawberry
from typing import List
from strawberry.fastapi import GraphQLRouter
from strawberry.scalars import JSON
from typing import  Optional


@strawberry.type
class UserType:
    id: str
    username: str
    email: str
    first_name:Optional[str] = None
    last_name:Optional[str] = None
    phone_no:Optional[str] = None
    role:Optional[str] = None
    createdOn:Optional[str] = None

@strawberry.input
class UserCreateInput:
    username: str
    email: str
    password: str
    first_name:Optional[str] = "null"
    last_name:Optional[str] = "null"

@strawberry.type
class AuthResponse:
    access_token: str
    refresh_token: str



@strawberry.type
class CaseType:
    id: str
    title:str
    description:str
    status:str
    created_by:str
    created_on:str
    assignee:str 
    status_change_reason:str = "Null"
    comment:str = "Null"
    watchers:Optional[str] = None
    updated_by:str  = "Null"
    updated_on:str  = "Null"


@strawberry.type
class CaseDistinctFields:
    result: JSON


@strawberry.type
class CaseStatusType:
    category: str = "Null"
    count: int = 0
      

@strawberry.type
class Query:
    @strawberry.field
    async def get_cases(self)->List[CaseType]:
        pass


query_schema = strawberry.Schema(query=Query)
query_router = GraphQLRouter(query_schema)
