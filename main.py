from fastapi import FastAPI, status, HTTPException
from uuid import uuid4
from typing import List
from sqlalchemy.exc import IntegrityError

from auth import auth
from auth.auth import user_dependency
from user_actions import user_actions
from databases.database import db_dependency, Base, engine
from helpers.check_logged_in import check_logged_in
from models.models import Post, CreatePost, ShowPosts, Users
from helpers.is_empty import is_empty

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(user_actions.router)

TITLE_MIN_CHAR_COUNT: int = 12
POST_DATA_MIN_WORD_COUNT: int = 120

TITLE_MAX_CHAR_COUNT: int = 100
POST_DATA_MAX_WORD_COUNT: int = 300

@app.get('/')
async def show_posts(db: db_dependency, user: user_dependency) -> None:
    posts: List[Post] = db.query(Post).all()
    posts_to_show: List[ShowPosts] = []

    for post in posts:
        post_creator_id: str = post.creator_id
        post_id: str = post.id
        post_title: str = post.title

        user: Users = db.query(Users).filter(post_creator_id == Users.id).first()

        post_creator_username: str = user.username

        post_shows: ShowPosts = ShowPosts(
            id=post_id,
            title=post_title,
            creator_username=post_creator_username
        )

        posts_to_show.append(post_shows)

    return {'posts': posts_to_show}


@app.post('/launch_post')
async def root(db: db_dependency, user: user_dependency, create_post_request: CreatePost):
    check_logged_in(user=user)

    post_title: str = create_post_request.title
    post_data: str = create_post_request.post_data

    if len(post_title) < TITLE_MIN_CHAR_COUNT and len(post_title) > TITLE_MAX_CHAR_COUNT:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail='can not accept the title'
        )

    if len(post_data.split()) < POST_DATA_MIN_WORD_COUNT and len(post_data.split()) > POST_DATA_MAX_WORD_COUNT:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail='can not accept the post data'
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

@app.put('/update_post/{post_id}')
async def update_post(post_id: str, db: db_dependency, user: user_dependency, updated_title: str) -> dict:
    check_logged_in(user=user)

    post: Post = db.query(Post).filter(post_id == Post.id).first()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='the id could not be found'
        )

    if post.creator_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='the id could not be found'
        )

    if len(updated_title) < TITLE_MIN_CHAR_COUNT or len(updated_title) > TITLE_MAX_CHAR_COUNT:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail='could not accept title'
        )

    updated_post: Post = Post(
        id=post.id,
        creator_id=user.id,
        post_data=post.post_data,
        title=updated_title
    )

    try:
        db.add(updated_post)
        db.commit(updated_post)
        db.refresh(updated_post)
        return {'updated_password'}
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail='the title given already exists'
        )
