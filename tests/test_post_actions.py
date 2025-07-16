from httpx import Response

from databases.database import open_db, Base
from databases.database_test import open_test_db, engine, TestSessionLocal
from helpers.api_requests_helper import ApiRequestsHelper
from auth.auth import get_current_user
from main import app
from models.models import Users

api_requests_helper: ApiRequestsHelper = ApiRequestsHelper()

app.dependency_overrides[get_current_user] = api_requests_helper.generate_mock_user
app.dependency_overrides[open_db] = open_test_db

def setup_function() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestSessionLocal()
    mock_user: Users = api_requests_helper.generate_mock_user()

    db.add(mock_user)
    db.commit()

test_post_data: str = "If you're looking for random paragraphs, you've come to the right place. When a random word or a random sentence isn't quite enough, the next logical step is to find a random paragraph. We created the Random Paragraph Generator with you in mind. The process is quite simple. Choose the number of random paragraphs you'd like to see and click the button. Your chosen number of paragraphs will instantly appear."
test_post_title: str = "amazing curiosity fr fr"
test_comment_body: str = 'test comment'

def test_view_comments_if_comments_are_empty() -> None:
    create_post_response: Response = api_requests_helper.add_post_request(post_data=test_post_data, title=test_post_title)
    assert create_post_response.status_code == 200

    post_id: str = create_post_response.json().get('post').get('id')
    view_comments_response: Response = api_requests_helper.view_comments_request(post_id=post_id)

    assert view_comments_response.status_code == 200
    assert view_comments_response.json().get('post_comments') == []

def test_view_comments_if_comments_are_full() -> None:
    create_post_response: Response = api_requests_helper.add_post_request(post_data=test_post_data, title=test_post_title)
    assert create_post_response.status_code == 200

    post_id: str = create_post_response.json().get('post').get('id')

    for index in range(3):
        add_comment_response: Response = api_requests_helper.add_comment_request(post_id=post_id, comment_body=test_comment_body)
        assert add_comment_response.status_code == 200

        view_comments_response: Response = api_requests_helper.view_comments_request(post_id=post_id)

        comment_body: str = view_comments_response.json().get('post_comments')[index].get('body')
        comment_creator_id: str = view_comments_response.json().get('post_comments')[index].get('creator_id')
        comment_mother_post_id: str = view_comments_response.json().get('post_comments')[index].get('mother_post_id')


        assert view_comments_response.status_code == 200
        assert comment_body == test_comment_body
        assert comment_creator_id == 'test_id'
        assert comment_mother_post_id == post_id

def test_view_comments_if_post_id_is_incorrect() -> None:
    view_comments_response: Response = api_requests_helper.view_comments_request(post_id='i_am_not_an_actual_post_id')
    assert view_comments_response.status_code == 404

def test_add_comment_if_input_is_correct() -> None:
    create_post_response: Response = api_requests_helper.add_post_request(post_data=test_post_data, title=test_post_title)
    assert create_post_response.status_code == 200

    post_id: str = create_post_response.json().get('post').get('id')
    add_comment_response: Response = api_requests_helper.add_comment_request(post_id=post_id, comment_body=test_comment_body)

    comment_body: str = add_comment_response.json().get('comment').get('body')
    comment_creator_id: str = add_comment_response.json().get('comment').get('creator_id')
    comment_mother_post_id: str = add_comment_response.json().get('comment').get('mother_post_id')

    assert add_comment_response.status_code == 200
    assert comment_body == test_comment_body
    assert comment_creator_id == 'test_id'
    assert comment_mother_post_id == post_id

def test_add_comment_if_input_is_incorrect() -> None:
    create_post_response: Response = api_requests_helper.add_post_request(post_data=test_post_data, title=test_post_title)
    assert create_post_response.status_code == 200

    post_id: str = create_post_response.json().get('post').get('id')

    wrong_comment_inputs: list[str] = ['     ', 'The internet is the most recent man-made creation that connects the world. The world has narrowed down after the invention of the internet. It has demolished all boundaries, which were the barriers between people and has made everything accessible. The internet is helpful to us in different ways. It is beneficial for sharing information with people in any corner of the world. It is also used in schools, government and private offices, and other public spaces. We stay connected to our close ones and share all the recent and live news with the help of the internet. Sitting in our homes, we know about all that’s happening around the world with a click or a swipe. The internet gives an answer to almost every question and touches every aspect of our lives. this is too long to be good you know']

    for wrong_comment_input in wrong_comment_inputs:
        add_comment_response: Response = api_requests_helper.add_comment_request(post_id=post_id, comment_body=wrong_comment_input)
        assert add_comment_response.status_code == 406

def test_add_comment_if_post_id_is_incorrect() -> None:
    add_comment_response: Response = api_requests_helper.add_comment_request(post_id='i_am_not_an_actual_post_id', comment_body=test_comment_body)
    assert add_comment_response.status_code == 404

def test_update_comment() -> None:
    create_post_response: Response = api_requests_helper.add_post_request(post_data=test_post_data, title=test_post_title)
    assert create_post_response.status_code == 200

    post_id: str = create_post_response.json().get('post').get('id')
    add_comment_response: Response = api_requests_helper.add_comment_request(post_id=post_id, comment_body=test_comment_body)

    assert add_comment_response.status_code == 200

    updated_comment: str = 'test updated comment'
    comment_id: str = add_comment_response.json().get('comment').get('id')

    update_comment_response: Response = api_requests_helper.update_comment_request(comment_id=comment_id,  updated_comment_body=updated_comment)

    assert update_comment_response.status_code == 200

def test_delete_comment() -> None:
    create_post_response: Response = api_requests_helper.add_post_request(post_data=test_post_data, title=test_post_title)
    assert create_post_response.status_code == 200

    post_id: str = create_post_response.json().get('post').get('id')
    add_comment_response: Response = api_requests_helper.add_comment_request(post_id=post_id, comment_body=test_comment_body)

    assert add_comment_response.status_code == 200

    comment_id: str = add_comment_response.json().get('comment').get('id')

    delete_comment_response: Response = api_requests_helper.delete_comment_request(comment_id=comment_id)

    assert delete_comment_response.status_code == 200
