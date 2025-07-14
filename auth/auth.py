from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from uuid import uuid4
from sqlalchemy.exc import IntegrityError
from typing import Optional

from models.models import Users, CreateUserRequest
from databases.database import db_dependency

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = 'f4c55231b48e36f7508d8856697af1b16368f67b6fe1ba54e26926fc83c104d1052fade6'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='/auth/token')

@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    """
    adds a new user account takes in a username and password and provides a user id (uuid4)

    PARAMETERS:
        db (db_dependency): the database for the program
        create_user_request (CreateUserRequest): the data model to follow when creating the account (raw JSON) the password and username must be special per user

    EXAMPLE:
        >>> https://base_link.com/auth json={username: <username>, password: <password>}
        output -> { user_attributes }
    """
    if len(create_user_request.username.split()) == 0 or len(create_user_request.password.split()) == 0:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail='can not accept an empty username or password'
        )

    created_user_model: Users = Users(
        id=str(uuid4()),
        username=create_user_request.username,
        hashed_password=bcrypt_context.hash(create_user_request.password)
    )

    try:
        db.add(created_user_model)
        db.commit()
        db.refresh(created_user_model)
        return {"created_user": created_user_model}
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail='can not have duplicate usernames or passwords'
        )

@router.post('/token', status_code=status.HTTP_200_OK)
async def login_for_access(form_request: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    """
    sign in the user into their account by generating a jwt token

    PARAMETERS:
        form_request (Annotated[OAuth2PasswordRequestForm, Depends()]): the username and password which must exist (have an account with their data)
        db (db_dependency): the database for the program

    EXAMPLE:
        >>> https://base_link.com/auth/token form_request=<username>, <password>
        output -> {'access_token': <token>, 'token_type': 'bearer'}
    """
    user: Optional[bool] = authenticate_user(form_request.username, form_request.password, db)

    if user is False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate user'
        )
    token = create_access_token(user.username, user.id, timedelta(minutes=20))
    return {'access_token': token, 'token_type': 'bearer'}

def authenticate_user(username: str, password: str, db: db_dependency) -> Optional[bool]:
    """
    checks if the user entered the correct username and password

    PARAMETERS:
        username (str): the username to login with which must exist in the database
        password (str): the password to login with which must exist in the database

    EXAMPLE:
        >>> authenticate_user(username=<username>, password=<password>)
        example return -> <user_info>
    """
    user = db.query(Users).filter(username == Users.username).first()

    if not user:
        return False
    if bcrypt_context.verify(password, user.hashed_password) is False:
        return False
    return user

def create_access_token(username: str, user_id: str, expires_delta: timedelta):
    """
    creates the jwt token (access token)
    
    PARAMETERS:
        username (str): the username to use when creating the token
        user_id (str): the user id to use when creating the token
        expires_delta (timedelta): the currect date/time to create the exiry date of the token

    EXAMPLE:
        >>> create_access_token(username=<username>, user_id=<user_id>, expires_delta=<expires_delta>)
        returns -> <jwt_token>
    """
    encode = {'sub': username, 'id': user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)], db: db_dependency):
    """
    gets the currect user data if they are logged in
    
    PARAMETERS:
        token (Annotated[str, Depends(oauth2_bearer)]): the created jwt token (access token)
        db (db_dependency): the database for the program

    EXAMPLE:
        >>> get_current_user(token=<token>)
        returns -> <user>
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get('sub')
        user_id = payload.get('id')
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='could not validate user'
            )
        user = db.query(Users).filter(user_id == Users.id).first()
        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate user'
        )

user_dependency = Annotated[Users, Depends(get_current_user)]
