from fastapi import FastAPI, status, HTTPException
from uuid import uuid4
from typing import List
from sqlalchemy.exc import IntegrityError

from auth import auth
from auth.auth import user_dependency
from post_actions import post_actions
from user_actions import user_actions
from databases.database import db_dependency, Base, engine
from helpers.check_logged_in import check_logged_in
from models.models import Comment, Post, CreatePost
from helpers.is_empty import is_empty

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(user_actions.router)
app.include_router(post_actions.router)

POST_DATA_MIN_WORD_COUNT: int = 30
POST_DATA_MAX_WORD_COUNT: int = 100

TITLE_MIN_CHAR_COUNT: int = 12
TITLE_MAX_CHAR_COUNT: int = 100

@app.get('/')
async def show_posts(db: db_dependency, user: user_dependency) -> None:
    """ queries all the posts and returns them """
    posts: List[Post] = db.query(Post).all()

    return {'posts': posts}


@app.post('/create_post')
async def create_post(db: db_dependency, user: user_dependency, create_post_request: CreatePost) -> None:
    """
    creates a post

    :param create_post_request = a request model containing the title (special per post) and body

    raises a 406 if the create_post_request has something wrong

    :example >>> https://base_link.com/create_post json={"post_data": <post_data>, "title": <post_title>}
    """
    check_logged_in(user=user)

    post_title: str = create_post_request.title
    post_data: str = create_post_request.post_data

    if is_empty(post_title) is True:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="can not accept an empty title"
        )

    if len(post_title) < TITLE_MIN_CHAR_COUNT or len(post_title) > TITLE_MAX_CHAR_COUNT:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail='can not accept the title'
        )

    if len(post_data.split()) < POST_DATA_MIN_WORD_COUNT or len(post_data.split(' ')) > POST_DATA_MAX_WORD_COUNT:
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
async def update_post(post_id: str, db: db_dependency, user: user_dependency, updated_title: str) -> None:
    """
    updates an existing post's title

    :param post_id = the post id to modify the post at it
    :param updated_title = a new title (must be special per post)

    raises 404 if post_id is not found
    raises 406 if updated_title has an incorrect value

    :example >>> https://base_link.com/update_post/<post_id>?updated_title=<updated_title>
    """
    check_logged_in(user=user)

    post: Post = db.query(Post).filter(post_id == Post.id).first()

    if post is None or post.creator_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='the id could not be found'
        )

    if is_empty(updated_title) is True:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail='can not accept an empty title'
        )

    if len(updated_title) < TITLE_MIN_CHAR_COUNT or len(updated_title) > TITLE_MAX_CHAR_COUNT:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail='could not accept title'
        )

    post.title = updated_title

    try:
        db.add(post)
        db.commit()
        db.refresh(post)

        return {'updated_post': post}
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail='the title given already exists'
        )

@app.delete('/delete_post/{post_id}')
async def delete_post(post_id: str, db: db_dependency, user: user_dependency) -> None:
    """
    delets a post by its id

    :param post_id = to delete the post at it

    raises 404 if post_id is not found

    :example >>> https://base_link.com/delete_post/<post_id>
    """
    post: Post = db.query(Post).filter(post_id == Post.id).first()

    if post is None or post.creator_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='the id could not be found'
        )

    deleted_post: Post = post

    db.query(Post).filter(post_id == Post.id).delete()
    db.query(Comment).filter(Comment.mother_post_id == post.id).delete()
    db.commit()

    return {"deleted_post": deleted_post}
