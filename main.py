from fastapi import FastAPI
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Request, Depends, status, Header
from typing import List, Optional, Dict ,Any, Union
from bson import ObjectId
from app.models.users.user import User,UserUpdate,UserCreate, Token, TokenData
from lib.host_manager import HostDatabaseManager
from app.database import get_database_atlas
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt,JWTError
from typing_extensions import Annotated
from fastapi.openapi.utils import get_openapi


# Apply the middleware
# from lib.middleware.s3Log import log_request_and_upload_to_s3_middle

from app.models.users.route import router as users_router
from app.models.bills.route import router as bills_router
from app.models.certifications.route import router as certifications_router
from app.models.contents.route import router as contents_routers
from app.models.courses.route import router as courses_router
from app.models.documents.route import router as documents_router
from app.models.enrolls.route import router as enrolls_router
from app.models.exams.route import router as exams_router
from app.models.forms.route import router as forms_router
from app.models.hosts.route import router as hosts_router
from app.models.mcourses.route import router as mcourses_router
from app.models.players.route import router as players_router
from app.models.posts.route import router as posts_router
from app.models.progresses.route import router as progresses_router
from app.models.questions.route import router as questions_router
from app.models.queues.route import router as queues_router
from app.models.schools.route import router as schools_router
from app.models.scores.route import router as scores_router
from app.models.storages.route import router as storages_router
from app.models.templates.route import router as templates_router
from app.models.transactions.route import router as transactions_router




# from app.models.items.route import router as items_router
# from app.models.shops.route import router as shops_router
print("print from main")
# mongol part
app = FastAPI()


# Apply the middleware


app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(bills_router, prefix="/bills", tags=["bills"])
app.include_router(certifications_router, prefix="/certifications", tags=["certifications"])
app.include_router(contents_routers, prefix="/contents", tags=["contents"])
app.include_router(courses_router, prefix="/courses", tags=["courses"])
app.include_router(documents_router, prefix="/documents", tags=["documents"])
app.include_router(enrolls_router, prefix="/enrolls", tags=["enrolls"])
app.include_router(exams_router, prefix="/exams", tags=["exams"])
app.include_router(forms_router, prefix="/forms", tags=["forms"])
app.include_router(hosts_router, prefix="/hosts", tags=["hosts"])
app.include_router(mcourses_router, prefix="/mcourses", tags=["mcourses"])
app.include_router(players_router, prefix="/players", tags=["players"])
app.include_router(posts_router, prefix="/posts", tags=["posts"])
app.include_router(progresses_router, prefix="/progresses", tags=["progresses"])
app.include_router(questions_router, prefix="/questions", tags=["questions"])
app.include_router(queues_router, prefix="/queues", tags=["queues"])
app.include_router(schools_router, prefix="/schools", tags=["schools"])
app.include_router(scores_router, prefix="/scores", tags=["scores"])
app.include_router(storages_router, prefix="/storages", tags=["storages"])
app.include_router(templates_router, prefix="/templates", tags=["templates"])
app.include_router(transactions_router, prefix="/transactions", tags=["transactions"])
app.include_router(scores_router, prefix="/scores", tags=["scores"])
app.include_router(scores_router, prefix="/scores", tags=["scores"])

# app.middleware("http")(log_request_and_upload_to_s3_middle) 

# app.include_router(items_router, prefix="/items", tags=["items"])
# app.include_router(shops_router, prefix="/shops", tags=["shops"])


# ---------- My autherize Swagger ----------
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.openapi.models import OAuthFlowAuthorizationCode as OAuthFlowAuthorizationCodeModel
from fastapi.openapi.models import OAuthFlowPassword as OAuthFlowPasswordModel
from fastapi.openapi.models import OAuthFlowImplicit as OAuthFlowImplicitModel
from fastapi.openapi.models import OAuthFlowClientCredentials as OAuthFlowClientCredentialsModel
from fastapi.openapi.models import OAuthFlowAuthorizationCode as OAuthFlowAuthorizationCodeModel
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.openapi.models import OAuthFlowPassword as OAuthFlowPasswordModel
from fastapi.openapi.models import OAuthFlowAuthorizationCode as OAuthFlowAuthorizationCodeModel

# # Define your OAuth2 flows
# oauth_flows = OAuthFlowsModel(
#     password=OAuthFlowPasswordModel(tokenUrl="/token"),
#     authorizationCode=OAuthFlowAuthorizationCodeModel(
#         authorizationUrl="/auth", tokenUrl="/token"
#     ),
#     clientCredentials=OAuthFlowClientCredentialsModel(tokenUrl="/token"),
#     implicit=OAuthFlowImplicitModel(authorizationUrl="/auth"),
# )

# # Add the OAuth2 security scheme
# security_schemes = {
#     "OAuth2PasswordBearer": {
#         "type": "oauth2",
#         "flows": oauth_flows,
#     }
# }

# app.openapi = {"security": [{"OAuth2PasswordBearer": []}], "info": {"title": "Your API"}}

# ------------------- Auth System ----------------

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

atlas_uri = "mongodb+srv://doadmin:AU97Jfe026gE415o@db-mongodb-kornxecobz-8ade0110.mongo.ondigitalocean.com/admin?tls=true&authSource=admin"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
database_manager = HostDatabaseManager("users")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user( username: str, password: str, htoken: str):
    host = htoken
    collection = database_manager.get_collection(host)
    user = collection.find_one({"username": username})
    if not user:
        return False
    if not verify_password(password, user['password']):
        return False
    return user

def authenticate_user_email( email: str, password: str):
    collection = get_database_atlas("WEIS", atlas_uri)["users"]
    user = collection.find_one({"email": email})
    if not user:
        return False
    if not verify_password(password, user['password']):
        return False
    return user

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(email=username)
    except JWTError:
        raise credentials_exception
    collection = get_database_atlas("WEIS", atlas_uri)["users"]
    user = collection.find_one({"email": token_data.email})
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    htoken: Optional[str] = Header(None, description="HToken for additional authentication")
):
    user = authenticate_user(form_data.username, form_data.password,htoken)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user['username']}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# ------------------ API part ------------
# Search

@app.post("/{collection}/aggregate")
async def aggregate_collection(
    collection: str,
    request_data: dict,
    htoken: Optional[str] = Header(None)
):
    try:
        pipeline = request_data.get("pipeline", [])

        if not isinstance(pipeline, list):
            raise HTTPException(status_code=400, detail="Invalid request format")

        # Get the database name based on the host or token
        database_name = database_manager.get_database_name(htoken)

        if not database_name:
            raise HTTPException(status_code=404, detail="Database not found for the host")

        # Get the collection based on the collection name and database name
        db_collection = database_manager.get_collection(htoken, collection)

        # Apply additional modifications to the pipeline as needed
        modified_pipeline = []
        for stage in pipeline:
            if "$match" in stage and "_id" in stage["$match"]:
                stage["$match"]["_id"] = ObjectId(stage["$match"]["_id"])
            modified_pipeline.append(stage)

        result = list(db_collection.aggregate(modified_pipeline))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/register", response_model=User)
async def register_user(
    user_data: UserCreate ,
    htoken: Optional[str] = Header(None)
    ):

    host = htoken
    collection = database_manager.get_collection(host)
    user_data_dict = user_data.dict()
    user_data_dict["password"] = get_password_hash(user_data_dict["password"])
    result = collection.insert_one(user_data_dict)
     
    if result.acknowledged:
        created_user = collection.find_one({"_id": ObjectId(result.inserted_id)})
        return User(**created_user)
    else:
        raise HTTPException(status_code=500, detail="Failed to create user")


@app.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user






# ------------------------ LINE ----------------------------------

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from app.database import get_database_atlas, pwd_context  # Import necessary dependencies
from fastapi import FastAPI, Depends, HTTPException
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.openapi.models import OAuthFlowAuthorizationCode
from lib.middleware.LINE import fetch_line_user_info


# app = FastAPI()

# Define your OAuth2 flow for LINE Login
line_oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="LINE_LOGIN_AUTH_URL",
    tokenUrl="LINE_TOKEN_URL",
)

# Callback endpoint for LINE Login
@app.get("/login/line/callback")
async def line_login_callback(
    code: str, 
    state: str,
    htoken: Optional[str] = Header(None) ,
    token: str = Depends(line_oauth2_scheme),
):
    try:
        # Use the LINE code to fetch the user information from LINE
        line_user_info = fetch_line_user_info(code)

        # Extract necessary information from LINE user info
        line_user_id = line_user_info.get("user_id")
        line_user_email = line_user_info.get("email")
        line_user_name = line_user_info.get("display_name")

        # Perform user registration or login logic based on LINE user information
        # Example: Check if the user is already registered in your system
        host = htoken
        collection = database_manager.get_collection(host)
        existing_user = collection.find_one({"line_user_id": line_user_id})

        if existing_user:
            # User is already registered, perform login
            user = authenticate_user(line_user_id, None, htoken=None)
        else:
            # User is not registered, perform registration
            user_data = {
                "username": line_user_name,
                "email": line_user_email,
                "line_user_id": line_user_id,
                # Add other required fields
            }
            result = collection.insert_one(user_data)

            if result.acknowledged:
                user = collection.find_one({"_id": ObjectId(result.inserted_id)})
            else:
                raise HTTPException(status_code=500, detail="Failed to create user")

        # Generate an access token for the user
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": user['username']}, expires_delta=access_token_expires)

        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# Run the app
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)