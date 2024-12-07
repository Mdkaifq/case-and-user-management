import strawberry
from .models import Role, User as UserModel
from .schema import UserType, UserCreateInput, AuthResponse
from strawberry.fastapi import GraphQLRouter
from fastapi import Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from .user_query import GetUserByIdQuery
from .db import get_db
from .auth import *
import uuid

async def get_context(session: AsyncSession = Depends(get_db))->str:
    return  {'session': session}

async def get_context2(request: Request, session: AsyncSession = Depends(get_db))->str:
    return  {'session': session, 'userId': request.path_params["userId"]}

@strawberry.type
class Mutation:

    @strawberry.mutation
    async def register(self, user_input: UserCreateInput, info :  strawberry.Info) -> UserType:
        # Check if user already exists
        db = info.context['session']
        stmt = select(UserModel).where(UserModel.username==user_input.username)
        existing_user = await db.execute(stmt)
        existing_user = existing_user.fetchall()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered"
            )
        
        # Create new user
        new_user = UserModel(
            username=user_input.username,
            email=user_input.email,
            hashed_password=UserModel.hash_password(user_input.password),
            first_name = user_input.first_name,
            last_name = user_input.last_name
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        return UserType(id=new_user.id, username=new_user.username, email=new_user.email, first_name=new_user.first_name, last_name=new_user.last_name, role=new_user.role, createdOn=new_user.created_on)
    

    @strawberry.mutation(permission_classes=[IsAunthenticated])
    async def update_user(self, email:str, first_name:str, last_name:str, phone_no:str, info: strawberry.Info)->UserType:

        user_id = info.context["request"].query_params.get("id")

        user_id = uuid.UUID(user_id)

        session = info.context["session"]

        user = await session.get(UserModel, user_id)

        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.phone_no = phone_no


        await session.commit()
        await session.refresh(user)

        return UserType(id=user.id, username=user.username, first_name=user.first_name, email=user.email, phone_no=user.phone_no, last_name=user.last_name)
    

    

@strawberry.type
class LoginMutation:
    @strawberry.mutation
    async def login(self, username: str, password: str, info :  strawberry.Info) -> AuthResponse:
        # Find user
        db = info.context['session']
        user = await db.execute(select(UserModel).filter(UserModel.username == username))
        user = user.scalar_one_or_none()
        
        if not user or not user.verify_password(password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        # Create access token
        access_token = create_access_token(
            data={"sub": user.username, "id": str(user.id), "token_type":"access"}, 
            expires_delta=timedelta(days=1)
        )

        refresh_token = create_access_token(
            data={"sub": user.username, "id": str(user.id), "token_type":"refresh"}, 
            expires_delta=timedelta(days=2)
        )
        
        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )


@strawberry.type
class AssignRoleMutation:
    @strawberry.mutation(permission_classes=[IsAdmin])
    async def assign_role(self, role:str, info: strawberry.Info)->UserType:

        user_id = info.context["userId"]

        user_id = uuid.UUID(user_id)

        session = info.context["session"]

        user = await session.get(UserModel, user_id)

        if role == 'admin':
            user.role = Role.ADMIN

        elif role == 'user':
            user.role = Role.USER

        else:
            raise HTTPException(status_code=422, detail="invalid choice.")

        await session.commit()
        await session.refresh(user)

        return UserType(id=user.id, username=user.username, first_name=user.first_name, email=user.email, phone_no=user.phone_no, last_name=user.last_name, role=user.role)


@strawberry.type
class ResetPasswordMutation:
    @strawberry.mutation
    async def reset_password(self, username: str, newPassword: str, oldPassword: str, info :  strawberry.Info) -> str:

        db = info.context['session']
        user = await db.execute(select(UserModel).filter(UserModel.username == username))
        user = user.scalar_one_or_none()
        
        if not user or not user.verify_password(oldPassword):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        if newPassword == oldPassword:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="new password can not be same as the old password"
            )
        
        user.hashed_password = UserModel.hash_password(newPassword)
        await db.commit()
        await db.refresh(user)

        return "message: your password has been updated successfully, status:200 OK"
    

@strawberry.type
class RefreshAccessTokenMutation:
    @strawberry.mutation
    async def refresh_access_token(self, info: strawberry.Info) -> AuthResponse:
        refresh_token = info.context['request'].headers.get('Refresh Token', '').replace('Bearer ', '')
        payload = verify_refresh_token(refresh_token)
        if payload:
            username = payload.get("sub")
            id = payload.get("id")
            access_token = create_access_token(
                data={"sub": username, "id": str(id), "token_type":"access"}, 
                expires_delta=timedelta(days=1)
            )

            refresh_token = create_access_token(
                data={"sub": username, "id": str(id), "token_type":"refresh"}, 
                expires_delta=timedelta(days=2)
            )
            
            return AuthResponse(
                access_token=access_token,
                refresh_token=refresh_token
            )
        else:

            return AuthResponse(
                access_token="Null",
                refresh_token="Null")

@strawberry.type
class DeleteUserMutation:
    @strawberry.mutation(permission_classes=[IsAdmin])
    async def delete_user(self, info: Info)->UserType:
        session = info.context["session"]
        request = info.context["request"]
        user_id = request.path_params["userId"]
        print("*************************************")
        print(user_id)
        print("*************************************")
        user_id = uuid.UUID(user_id)
        user = await session.get(UserModel, user_id)
        response_user = UserType(id=user.id, username=user.username, first_name=user.first_name, email=user.email, phone_no=user.phone_no, last_name=user.last_name, role=user.role)
        await session.delete(user)
        await session.commit()
        return response_user
    

@strawberry.type
class EmptyQuery:
    placeholder:str = "This is an empty query"

register_and_update_user_schema = strawberry.Schema(query=GetUserByIdQuery, mutation=Mutation)
register_and_update_user_router = GraphQLRouter(register_and_update_user_schema, context_getter=get_context)

login_schema = strawberry.Schema(query=EmptyQuery, mutation=LoginMutation)
login_router = GraphQLRouter(login_schema, context_getter=get_context)

assign_role_schema = strawberry.Schema(query=EmptyQuery, mutation=AssignRoleMutation)
assign_role_router = GraphQLRouter(assign_role_schema, context_getter=get_context2)

reset_password_schema = strawberry.Schema(query=EmptyQuery, mutation=ResetPasswordMutation)
reset_password_router = GraphQLRouter(reset_password_schema, context_getter=get_context)

refresh_access_token_schema = strawberry.Schema(query=EmptyQuery, mutation=RefreshAccessTokenMutation)
refresh_access_token_router = GraphQLRouter(refresh_access_token_schema)

delete_user_schema = strawberry.Schema(query=EmptyQuery, mutation=DeleteUserMutation)
delete_user_router = GraphQLRouter(delete_user_schema, context_getter=get_context)