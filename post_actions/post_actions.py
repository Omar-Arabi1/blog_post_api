from fastapi import APIRouter, HTTPException, status
from uuid import uuid4

from helpers.check_logged_in import check_logged_in
from helpers.is_empty import is_empty
from auth.auth import user_dependency
from databases.database import db_dependency
from models.models import Comment, Post

router = APIRouter(
    prefix='/post',
    tags=['post']
)

COMMENT_MAX_WORD_COUNT: int = 100

@router.get('/view_comments/{post_id}')
async def view_comments(post_id: str, db: db_dependency, user: user_dependency) -> None:
    check_logged_in(user=user)

    post: Post = db.query(Post).filter(Post.id == post_id).first()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='could not find post'
        )

    post_comments = db.query(Comment).filter(Comment.mother_post_id == post.id).all()

    return {'post_comments': post_comments}

@router.post('/add_comment/{post_id}')
async def create_comment(post_id: str, db: db_dependency, user: user_dependency, comment_body: str) -> None:
    check_logged_in(user=user)

    post: Post = db.query(Post).filter(Post.id == post_id).first()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='count not find the post'
        )

    if is_empty(comment_body) is True or len(comment_body.split()) > COMMENT_MAX_WORD_COUNT:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail='can not accept comment'
        )

    comment: Comment = Comment(
        id=str(uuid4()),
        body=comment_body,
        creator_id=user.id,
        mother_post_id=post_id
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return {"comment": comment}

@router.put('/update_comment/{comment_id}')
async def update_comment(comment_id: str, db: db_dependency, user: user_dependency, updated_comment_body: str) -> None:
    check_logged_in(user=user)

    comment: Comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if comment is None or comment.creator_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='could not find the comment'
        )

    if is_empty(text=updated_comment_body) is True or len(updated_comment_body.split()) > COMMENT_MAX_WORD_COUNT:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail='can not accept the updated comment'
        )

    comment.body = updated_comment_body
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return {'updated_comment': comment}

@router.delete('/delete_comment/{comment_id}')
async def delete_comment(comment_id: str, user: user_dependency, db: db_dependency) -> None:
    check_logged_in(user=user)

    comment: Comment = db.query(Comment).filter(Comment.id == comment_id).first()
    
    if comment is None or comment.creator_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='could not find the comment'
        )
        
    deleted_comment: Comment = comment

    db.query(Comment).filter(Comment.id == comment_id).delete()
    db.commit()

    return {'deleted_comment': deleted_comment}
    