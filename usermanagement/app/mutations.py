import strawberry
from .models import Case as CaseModel
from datetime import datetime, timezone
from .schema import CaseType
from strawberry.fastapi import GraphQLRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .db import get_db
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
        return CaseType(id=case.id, title=case.title, description=case.description, status=case.status, created_by=str(case.created_by), created_on=case.created_on, assignee=str(case.assignee))
    

@strawberry.type
class EmptyQuery:
    placeholder:str = "This is an empty query"


mutation_schema = strawberry.Schema(query=EmptyQuery, mutation=Mutation)
mutation_router = GraphQLRouter(mutation_schema, context_getter=get_context)
