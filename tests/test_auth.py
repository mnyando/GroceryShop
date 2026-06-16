import unittest
from app import create_app
from app.database import query_documents, delete_document
from flask import url_for

class TestAuthRegistration(unittest.TestCase):
    def setUp(self):
        self.app = create_app('test')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.test_usernames = []

    def tearDown(self):
        # Clean up any users created during tests
        for uname in self.test_usernames:
            docs = query_documents('users', 'username', '==', uname)
            for doc in docs:
                delete_document('users', doc['id'])
        self.app_context.pop()

    def test_registration_request(self):
        """Test submitting the registration form."""
        username = "test_form_user"
        self.test_usernames.append(username)
        
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['TESTING'] = True
        
        form_data = {
            'firstname': 'Test',
            'lastname': 'User',
            'username': username,
            'email': 'test_form_user@example.com',
            'role': 'customer',
            'password': 'password123',
            'password_confirm': 'password123'
        }
        
        response = self.client.post('/authenticate/register', data=form_data, follow_redirects=True)
        print("\n--- Registration Response ---")
        print(f"Status Code: {response.status_code}")
        self.assertEqual(response.status_code, 200)


class TestMainRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app('test')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_home_route(self):
        """Test that the root URL loads successfully."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sun-Ripened Tomatoes', response.data) # Carousel slide should be there

    def test_shop_route(self):
        """Test that the /shop URL loads successfully and contains catalog grid."""
        response = self.client.get('/shop')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Fresh Produce', response.data)
        self.assertIn(b'Search vegetables', response.data)

    def test_about_route(self):
        """Test that the /about URL loads successfully and contains details."""
        response = self.client.get('/about')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Mama Mboga', response.data)
        self.assertIn(b'Farm to Table', response.data)

if __name__ == '__main__':
    unittest.main()
