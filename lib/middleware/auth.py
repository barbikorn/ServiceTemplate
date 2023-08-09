from fastapi import Depends, HTTPException, APIRouter, Header
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import jwt


router = APIRouter()

class JWTAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, request, call_next):
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                user_id: str = payload.get("sub")
                if user_id is None:
                    raise HTTPException(status_code=401, detail="Invalid authentication credentials")
                request.state.user_id = user_id
            except JWTError:
                raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        else:
            raise HTTPException(status_code=401, detail="Missing authentication token")

        response = await call_next(request)
        return response


# Password hashing
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Secret key for JWT token
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

# Sample user database
users_db = [
    {
        "id": "1",
        "username": "user1",
        "password": "$2b$12$8ZG5t1WR7bvB9oncHl5DZu1D.NLmN7qZMIFwEm0oF3RYeUbbTovjO"  # Hashed password: "password1"
    },
    {
        "id": "2",
        "username": "user2",
        "password": "$2b$12$p.E8n.ZjnlYYuDM4PScqS.0lo3cGWeMH5zwqj7AVVlBROw2OO96NK"  # Hashed password: "password2"
    }
]

# Authenticate user based on username and password
def authenticate_user(username: str, password: str):
    for user in users_db:
        if user["username"] == username and verify_password(password, user["password"]):
            return user["id"]
    return None

# Verify password
def verify_password(plain_password, hashed_password):
    return password_context.verify(plain_password, hashed_password)

# Hash password
def get_password_hash(password):
    return password_context.hash(password)

# Create access token
def create_access_token(data: dict):
    to_encode = data.copy()
    access_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return access_token

# Login route
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password

    user_id = authenticate_user(username, password)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token({"sub": user_id})
    return {"access_token": access_token, "token_type": "bearer"}

# Registration route
@router.post("/register")
def register(username: str, password: str):
    # Check if username is already taken
    for user in users_db:
        if user["username"] == username:
            raise HTTPException(status_code=400, detail="Username already exists")

    # Hash password
    hashed_password = get_password_hash(password)

    # Generate user ID (replace with your own logic, e.g., UUID)
    user_id = str(len(users_db) + 1)

    # Add user to database
    user_data = {
        "id": user_id,
        "username": username,
        "password": hashed_password
    }
    users_db.append(user_data)

    return {"message": "User registered successfully"}

# Protected route example
@router.get("/protected")
def protected_route(user_id: str = Header(...)):
    # Perform authorization logic here, e.g., check if user ID is valid or has sufficient privileges
    # You can access the user ID from the request header

    # If authorization fails, raise an HTTPException
    raise HTTPException(status_code=403, detail="Not authorized")

# Other necessary authentication-related functions/routes can be
