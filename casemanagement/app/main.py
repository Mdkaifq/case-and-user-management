from fastapi import FastAPI, Request
from .schema import query_router
from .mutations import mutation_router, update_case_mutation_router
from . query import status_query_router, distinct_query_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(query_router, prefix="/graphql/get/cases")
app.include_router(mutation_router, prefix="/api/case/create")
app.include_router(update_case_mutation_router, prefix="/api/case/update")
app.include_router(status_query_router, prefix="/graphql/case-service/cases/states-count")
app.include_router(distinct_query_router, prefix="/graphql/api/v1/cases/{field}/distinct-values")

# @app.get("/graphql/api/v1/cases/{field}/distinct-values")
# async def distinct_field_endpoint(field : str, request: Request):

#     return await distinct_query_router.graphql(request=request)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Case Management System with FastAPI and YugabyteDB"}
