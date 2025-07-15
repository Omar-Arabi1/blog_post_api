from fastapi import FastAPI, status, HTTPException
from uuid import uuid4

from sqlalchemy.exc import IntegrityError

from auth import auth
from auth.auth import user_dependency
from user_actions import user_actions
from databases.database import db_dependency, Base, engine
from helpers.check_logged_in import check_logged_in
from models.models import Post, CreatePost
from helpers.is_empty import is_empty

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(user_actions.router)

@app.post('/post')
def root(db: db_dependency, user: user_dependency, create_post_request: CreatePost):
    check_logged_in(user=user)

    post_title: str = create_post_request.title
    post_data: str = create_post_request.post_data

    TITLE_MIN_CHAR_COUNT: int = 12
    POST_DATA_MIN_WORD_COUNT: int = 120

    if is_empty(post_title) is False or is_empty(post_data) is False:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail='can not accept empty data'
        )

    if len(post_title) < TITLE_MIN_CHAR_COUNT:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail='the title must at least be 12 characters'
        )

    if len(post_data.split()) < POST_DATA_MIN_WORD_COUNT:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail='the post must at least be 120 words'
        )

    post: Post = Post(
        id=str(uuid4()),
        creator_id=user.id,
        post_data=post_data,
        title=post_title
    )

    try:
        db.add(post)
        db.commit()
        db.refresh(post)

        return {"post": post}
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail='the title given already exists'
        )
