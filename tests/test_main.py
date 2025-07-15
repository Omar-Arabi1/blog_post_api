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

test_post_data: str = "Curiosity is the foundation of human progress, a driving force that has shaped history,"\
                      "science, art, and everyday life. It begins in childhood, where even the smallest questions—“Why is the sky blue?” or “How do birds fly?”—reflect our desire"\
                      "to understand the world around us. As we grow, curiosity becomes more than a simple urge; it becomes a habit of mind,"\
                      "a tool for exploration and learning. It fuels innovation, inspires creativity, and encourages"\
                      "empathy by leading us to consider perspectives different from our own. In science, it has led to groundbreaking discoveries; in philosophy, it challenges our deepest assumptions."\
                      "Curiosity keeps us engaged, alert, and adaptable in a rapidly"\
                      "changing world. It transforms uncertainty into opportunity and routine into revelation. When we nurture curiosity, we not only enhance our own lives, but also contribute to "\
                      "the advancement of society as a whole. In every question lies the seed of growth."

test_post_title: str = "amazing curiosity fr fr"

def setup_function() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestSessionLocal()
    mock_user: Users = api_requests_helper.generate_mock_user()

    db.add(mock_user)
    db.commit()

def test_list_posts() -> None:
    list_posts_response: Response = api_requests_helper.list_posts_request()
    
    assert list_posts_response.status_code == 200
    assert list_posts_response.json().get('posts') == []

def test_launch_post() -> None:
    launch_post_response: Response = api_requests_helper.add_post_request(post_data=test_post_data, title=test_post_title)
    
    assert launch_post_response.status_code == 200
