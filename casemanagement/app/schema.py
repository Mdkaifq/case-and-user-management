import strawberry
from typing import List
from strawberry.fastapi import GraphQLRouter
from strawberry.scalars import JSON
from typing import  Optional



@strawberry.type
class CaseType:
    id: str
    title:str
    description:str
    status:str
    created_by: str
    created_on:str
    assignee: str
    status_change_reason:str = "Null"
    comment:str = "Null"
    watchers:Optional[str] = None
    updated_by:str  = "Null"
    updated_on:str  = "Null"
    message:str 

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
