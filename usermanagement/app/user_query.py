from __future__ import annotations
import strawberry
from .models import Role, User as UserModel
from .schema import UserType, UserCreateInput, AuthResponse
from strawberry.fastapi import GraphQLRouter
from fastapi import Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from .db import get_db
from .auth import *
import uuid
from .mutations import get_context

@strawberry.type
class GetUserByIdQuery:
    @strawberry.field(permission_classes=[IsAunthenticated])
    async def get_user_by_id(self, info: strawberry.Info)->UserType:

        user_id = info.context["request"].query_params.get("id")

        user_id = uuid.UUID(user_id)

        session = info.context["session"]

        user = await session.get(UserModel, user_id)

        if not user:
            raise HTTPException(status_code=422, detail="incorrect id")

        return UserType(id=user.id, username=user.username, first_name=user.first_name, email=user.email, phone_no=user.phone_no, last_name=user.last_name, role=user.role)


    @strawberry.field(permission_classes=[IsAunthenticated])
    async def filter_users(self, createdOn: str, role:str, info: strawberry.Info)->list[UserType]:
        session = info.context["session"]

        if role == 'admin':
            role = Role.ADMIN
        else:
            role = Role.USER

        stmt = select(UserModel).where((UserModel.created_on.like(f'{createdOn}%')) & (UserModel.role == role))

        user = await session.execute(stmt)

        users = user.fetchall()

        return [UserType(id=row[0].id, username=row[0].username, email=row[0].email, first_name=row[0].first_name, last_name=row[0].last_name, role=str(row[0].role)[5:], createdOn=row[0].created_on) for row in users]


@strawberry.type
class GetAllUsersQuery:
    @strawberry.field(permission_classes=[IsAunthenticated])
    async def get_all_users(self, info: strawberry.Info)->list[UserType]:
        session = info.context["session"]

        stmt = select(UserModel)

        user = await session.execute(stmt)

        users = user.fetchall()

        return [UserType(id=row[0].id, username=row[0].username, email=row[0].email, first_name=row[0].first_name, last_name=row[0].last_name, role=str(row[0].role)[5:], createdOn=row[0].created_on) for row in users]
    

get_all_users_schema = strawberry.Schema(query=GetAllUsersQuery)
get_all_users_router = GraphQLRouter(get_all_users_schema, context_getter=get_context)