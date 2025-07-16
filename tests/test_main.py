from httpx import Response

from auth.auth import get_current_user
from helpers.api_requests_helper import ApiRequestsHelper
from main import app
from databases.database import open_db, Base
from databases.database_test import TestSessionLocal, open_test_db, engine
from models.models import Users

api_requests_helper: ApiRequestsHelper = ApiRequestsHelper()

app.dependency_overrides[get_current_user] = api_requests_helper.generate_mock_user
app.dependency_overrides[open_db] = open_test_db

test_post_data: str = "If you're looking for random paragraphs, you've come to the right place. When a random word or a random sentence isn't quite enough, the next logical step is to find a random paragraph. We created the Random Paragraph Generator with you in mind. The process is quite simple. Choose the number of random paragraphs you'd like to see and click the button. Your chosen number of paragraphs will instantly appear."

test_post_title: str = "amazing curiosity fr fr"

def setup_function() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestSessionLocal()
    mock_user: Users = api_requests_helper.generate_mock_user()

    db.add(mock_user)
    db.commit()

def test_list_posts_if_posts_is_empty() -> None:
    list_posts_response: Response = api_requests_helper.list_posts_request()

    assert list_posts_response.status_code == 200
    assert list_posts_response.json().get('posts') == []

def test_list_posts_if_posts_is_full() -> None:
    test_titles: list[str] = ['first test title', 'second test title', 'third test title']
    for index, title in enumerate(test_titles):
        add_post_response: Response = api_requests_helper.add_post_request(post_data=test_post_data, title=title)

        assert add_post_response.status_code == 200

        list_posts_response: Response = api_requests_helper.list_posts_request()
        post_creator_id: str = list_posts_response.json().get('posts')[index].get('creator_id')
        post_title: str = list_posts_response.json().get('posts')[index].get('title')
        post_data: str = list_posts_response.json().get('posts')[index].get('post_data')


        assert list_posts_response.status_code == 200
        assert post_creator_id == 'test_id'
        assert post_title == title
        assert post_data == test_post_data

def test_launch_post() -> None:
    launch_post_response: Response = api_requests_helper.add_post_request(post_data=test_post_data, title=test_post_title)

    assert launch_post_response.status_code == 200

def test_updated_post() -> None:
    launch_post_response: Response = api_requests_helper.add_post_request(post_data=test_post_data, title=test_post_title)

    assert launch_post_response.status_code == 200

    post_id: str = launch_post_response.json().get('post').get('id')

    updated_title: str = 'fake_updated_title'

    updated_post_response: Response = api_requests_helper.update_post_request(updated_title=updated_title, post_id=post_id)

    assert updated_post_response.status_code == 200

def test_delete_post() -> None:
    launch_post_response: Response = api_requests_helper.add_post_request(post_data=test_post_data, title=test_post_title)

    assert launch_post_response.status_code == 200

    post_id: str = launch_post_response.json().get('post').get('id')

    delete_post_response: Response = api_requests_helper.delete_post_request(post_id=post_id)

    assert delete_post_response.status_code == 200
    assert delete_post_response.json().get('deleted_post') == launch_post_response.json().get('post')
