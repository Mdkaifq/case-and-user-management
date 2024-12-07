import strawberry
from .models import Case as CaseModel
from datetime import datetime, timezone
from strawberry.types import Info
from .schema import CaseType
from strawberry.fastapi import GraphQLRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .db import get_db
import uuid
from .query import GetQuery
from .auth import IsAunthenticated, get_id_from_token

async def get_context(session: AsyncSession = Depends(get_db)):
    return {'session': session}

@strawberry.type
class Mutation:
    @strawberry.mutation(permission_classes=[IsAunthenticated])
    async def create_case(self, title:str, description:str, status:str, info: strawberry.Info)->CaseType:
        token = info.context['request'].headers.get('Authorization', '').replace('Bearer ', '')
        user_id = get_id_from_token(token)
        case = CaseModel(title=title, description=description, status=status, created_by=user_id, assignee=user_id, created_on=datetime.now(timezone.utc))
        session = info.context["session"]
        session.add(case)
        await session.commit()
        await session.refresh(case)
        return CaseType(id=case.id, title=case.title, description=case.description, status=case.status, created_by=case.created_by, created_on=case.created_on, assignee=case.assignee, message="case created successfully")



@strawberry.type
class UpdateCaseMutation:
    @strawberry.mutation

    async def update_case(self, description:str, status:str, info: strawberry.Info, status_change_reason:str, comment:str, watchers:int)->CaseType:
        session = info.context["session"]
        request = info.context["request"]
        case_id = request.query_params.get("id")
        case_id = uuid.UUID(case_id)
        case = await session.get(CaseModel, case_id)
        case.description = description
        case.status = status
        case.status_change_reason = status_change_reason
        case.comment = comment
        token = info.context['request'].headers.get('Authorization', '').replace('Bearer ', '')
        user_id = get_id_from_token(token)
        if case.watchers=="Null" or case.watchers is None:
            case.watchers = [watchers]
        else:
            watchers_list = case.watchers + [watchers]
            case.watchers = list(set(watchers_list))
        case.updated_by = user_id
        case.updated_on = datetime.now(timezone.utc)
        await session.commit()
        await session.refresh(case)
        return CaseType(id=case.id, title=case.title, description=case.description, created_by=case.created_by, created_on=case.created_on, status=case.status, updated_by=case.updated_by, updated_on=case.updated_on, assignee=case.assignee, status_change_reason=case.status_change_reason, watchers=str(case.watchers), comment=case.comment, message="case updated successfully" )
    
    @strawberry.mutation
    async def delete_case(self, info: strawberry.Info)->CaseType:
        session = info.context["session"]
        request = info.context["request"]
        case_id = request.query_params.get("id")
        case_id = uuid.UUID(case_id)
        case = await session.get(CaseModel, case_id)

        responseCase = case
        await session.delete(case)
        await session.commit()
        return CaseType(id=responseCase.id, title=responseCase.title, description=responseCase.description, status=responseCase.status, created_by=responseCase.created_by, assignee=responseCase.assignee, created_on=responseCase.created_on, message="case deleted successfully")


@strawberry.type
class EmptyQuery:
    placeholder:str = "This is an empty query"


mutation_schema = strawberry.Schema(query=EmptyQuery, mutation=Mutation)
mutation_router = GraphQLRouter(mutation_schema, context_getter=get_context)

update_case_mutation_schema = strawberry.Schema(query=GetQuery, mutation=UpdateCaseMutation)
update_case_mutation_router = GraphQLRouter(update_case_mutation_schema, context_getter=get_context)


