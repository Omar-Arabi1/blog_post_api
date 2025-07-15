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
    
    def update_post_request(self, updated_title: str, post_id: str) -> Response:
        return client.put(f'/update_post/{post_id}', params={'updated_title': updated_title}, headers={"Authorization": "fake-token"})
    
    def delete_post_request(self, post_id: str) -> Response:
        return client.delete(f'/delete_post/{post_id}', headers={"Authorization": "fake-token"})