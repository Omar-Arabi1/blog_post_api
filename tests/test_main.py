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

def test_create_post_if_data_is_correct() -> None:
    create_post_response: Response = api_requests_helper.add_post_request(post_data=test_post_data, title=test_post_title)

    post_creator_id: str = create_post_response.json().get('post').get('creator_id')
    post_data: str = create_post_response.json().get('post').get('post_data')
    post_title: str = create_post_response.json().get('post').get('title')

    assert create_post_response.status_code == 200
    assert post_creator_id == 'test_id'
    assert post_data == test_post_data
    assert post_title == test_post_title

def test_create_post_if_data_is_incorrect() -> None:
    wrong_post_data: list[str] = ['too short for success', '   ', 'The internet is the most recent man-made creation that connects the world. The world has narrowed down after the invention of the internet. It has demolished all boundaries, which were the barriers between people and has made everything accessible. The internet is helpful to us in different ways. It is beneficial for sharing information with people in any corner of the world. It is also used in schools, government and private offices, and other public spaces. We stay connected to our close ones and share all the recent and live news with the help of the internet. Sitting in our homes, we know about all that’s happening around the world with a click or a swipe. The internet gives an answer to almost every question and touches every aspect of our lives. basically this is longer than it should okay stop reading now and yes I stole this off of the internet okay!', test_post_data, '   ']

    wrong_titles: list[str] = ['to short', '     ', 'this is also very long this should not be over a hundered letters but guess what I am doing I am making it longer thatn it should because this is supposed to be wrong data you know do not you huh you are still reading this you are wasting your time go ahead and run the test already I am long enough', 'this is ..', test_post_title]

    for title, post_data in zip(wrong_titles, wrong_post_data):
        create_post_response: Response = api_requests_helper.add_post_request(post_data=post_data, title=title)

        assert create_post_response.status_code == 406

def test_update_post_if_input_is_correct() -> None:
    create_post_response: Response = api_requests_helper.add_post_request(post_data=test_post_data, title=test_post_title)
    assert create_post_response.status_code == 200

    post_id: str = create_post_response.json().get('post').get('id')

    updated_title: str = 'fake updated title'

    updated_post_response: Response = api_requests_helper.update_post_request(updated_title=updated_title, post_id=post_id)

    post_creator_id: str = updated_post_response.json().get('updated_post').get('creator_id')
    post_data: str = updated_post_response.json().get('updated_post').get('post_data')
    post_title: str = updated_post_response.json().get('updated_post').get('title')

    assert updated_post_response.status_code == 200
    assert post_creator_id == 'test_id'
    assert post_data == test_post_data
    assert post_title != test_post_title and post_title == updated_title

def test_update_post_if_input_is_incorrect() -> None:
    create_post_response: Response = api_requests_helper.add_post_request(post_data=test_post_data, title=test_post_title)
    assert create_post_response.status_code == 200

    post_id: str = create_post_response.json().get('post').get('id')

    wrong_updated_titles: list[str] = ['to short', '     ', 'this is also very long this should not be over a hundered letters but guess what I am doing I am making it longer thatn it should because this is supposed to be wrong data you know do not you huh you are still reading this you are wasting your time go ahead and run the test already I am long enough']

    for wrong_title in wrong_updated_titles:
        updated_post_response: Response = api_requests_helper.update_post_request(updated_title=wrong_title, post_id=post_id)
        assert updated_post_response.status_code == 406

def test_update_post_if_id_is_incorrect() -> None:
    non_existant_post_id: str = 'i_do_not_exist'

    updated_post_response: Response = api_requests_helper.update_post_request(updated_title='test updated title', post_id=non_existant_post_id)
    assert updated_post_response.status_code == 404

def test_delete_post() -> None:
    launch_post_response: Response = api_requests_helper.add_post_request(post_data=test_post_data, title=test_post_title)

    assert launch_post_response.status_code == 200

    post_id: str = launch_post_response.json().get('post').get('id')

    delete_post_response: Response = api_requests_helper.delete_post_request(post_id=post_id)

    assert delete_post_response.status_code == 200
    assert delete_post_response.json().get('deleted_post') == launch_post_response.json().get('post')
