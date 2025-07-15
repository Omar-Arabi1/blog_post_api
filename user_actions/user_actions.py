from fastapi import APIRouter, HTTPException, status

from auth.auth import user_dependency
from databases.database import db_dependency
from models.models import Post, ShowUser, Users
from helpers.check_logged_in import check_logged_in
from helpers.is_empty import is_empty

router = APIRouter(
    prefix='/account',
    tags=['account']
)

@router.get('/')
async def get_user(user: user_dependency, db: db_dependency) -> dict:
    check_logged_in(user=user)
    
    user: Users = db.query(Users).filter(user.id == Users.id).first()
    
    user_seriazable: ShowUser = ShowUser(
        id=user.id,
        username=user.username,
        hashed_password=user.hashed_password
    )
    
    return {'user': user_seriazable}

@router.put('/update_user/{username}')
async def update_user(user: user_dependency, db: db_dependency, username: str):
    """
    updates the user's username

    PARAMETERS:
        user (user_dependency): the user info to validate authentication
        db (db_dependency): the database for the program
        username (str): the username to update the old existing username (path parameter) the username mustn't be empty

    EXAMPLE:
        >>> https://base_link.com/me/update_user/<username>
        output -> None/null
    """
    check_logged_in(user=user)

    update_user = db.query(Users).filter(user.username == Users.username).first()

    if is_empty(update_user.username) is False:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail='can not take empty username'
        )

    update_user.username = username

    db.add(update_user)
    db.commit()

@router.delete('/delete_user')
async def delete_user(user: user_dependency, db: db_dependency):
    """
    deletes a user from the database

    PARAMETERS:
        user (user_dependency): the user info to validate authentication
        db (db_dependency): the database for the program

    EXAMPLE:
        >>> https://base_link.com/me/delete_user
        output -> None/null
    """
    check_logged_in(user=user)

    db.query(Users).filter(user.username == Users.username).delete()
    db.query(Post).filter(user.id == Post.creator_id).delete()
    db.commit()
