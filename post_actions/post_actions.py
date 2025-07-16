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
    """
    shows all the comments for a certain post by its id
    
    :param post_id = the post id to get its comments
    
    raises a 404 if id is not found
    
    :example >>> https://base_link.com/post/view_comments/<post_id>
    """
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
    """
    adds a comment to a post by its id
    
    :param post_id = the post id to comment on
    :param comment_body = the updated comment body
    
    raises a 404 if post_id is not found
    
    :example >>> https://base_link.com/post/add_comment/<post_id>?comment_body=<comment_body>
    """
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
    """
    updates an existing comment by the comment's id
    
    :param comment_id = the id of the comment to update
    :param updated_comment_body = the updated comment body
    
    raises a 404 if id is not found
    raises a 406 if the updated comment body has something wrong
    
    :example >>> https://base_link.com/post/update_comment/<comment_id>?updated_comment_body=<updated_comment_body>
    """
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
    """
    deletes an existing comment by its id
    
    :param comment_id = the comment id to delete
    
    raises a 404 if id not found
    
    :example >>> https://base_link.com/post/delete_comment/<comment_id>
    """
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
    