from fastapi import APIRouter, HTTPException, status
from uuid import uuid4

from helpers.check_logged_in import check_logged_in
from helpers.is_empty import is_empty
from auth.auth import user_dependency
from databases.database import db_dependency
from models.models import Comment, Post, ShowComment

router = APIRouter(
    prefix='/post',
    tags=['post']
)

COMMENT_MAX_WORD_COUNT: int = 100

@router.post('/{post_id}')
async def create_comment(post_id: str, db: db_dependency, user: user_dependency, comment_body: str) -> None:
    check_logged_in(user=user)
    
    post: Post = db.query(Post).filter(Post.id == post_id).first()
    
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='count not find the post'
        )

    if is_empty(comment_body) is True:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail='can not accept an empty comment'
        )

    if len(comment_body.split()) > COMMENT_MAX_WORD_COUNT:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail='can not accept a comment that passes the max word count'
        )

    comment: Comment = Comment(
        id=str(uuid4()),
        body=comment_body,
        creator_id=user.id,
        mother_post_id=post_id
    )
    
    serializable_comment: ShowComment = ShowComment(
        id=comment.id,
        body=comment.body,
        creator_id=comment.creator_id,
        mother_post_id=comment.mother_post_id
    )
    
    db.add(comment)
    db.commit()
    
    return {"comment": serializable_comment}
    