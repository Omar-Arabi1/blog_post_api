from fastapi.testclient import TestClient
from httpx import Response
from models.models import Users
from main import app

client = TestClient(app)

class ApiRequestsHelper():
    def generate_mock_user(self) -> Users:
        return Users(
            id='test_id',
            username='test_username',
            hashed_password='test_hashed_password'
        )
    
    def list_posts_request(self) -> Response:
        return client.get('/', headers={"Authorization": "fake-token"})
        
    def add_post_request(self, post_data: str, title: str) -> Response:
        return client.post('/launch_post', json={'post_data': post_data, 'title': title}, headers={"Authorization": "fake-token"})