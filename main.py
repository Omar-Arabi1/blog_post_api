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
        

@app.post('/post')
async def root(db: db_dependency, user: user_dependency, create_post_request: CreatePost):
    check_logged_in(user=user)

    post_title: str = create_post_request.title
    post_data: str = create_post_request.post_data

    TITLE_MIN_CHAR_COUNT: int = 12
    POST_DATA_MIN_WORD_COUNT: int = 120
    
    TITLE_MAX_CHAR_COUNT: int = 100
    POST_DATA_MAX_WORD_COUNT: int = 300

    if is_empty(post_title) is False or is_empty(post_data) is False:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail='can not accept empty data'
        )

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
