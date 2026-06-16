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
        
        # We need a GET request first to retrieve the CSRF token if enabled (WTF_CSRF_ENABLED is usually disabled in tests, or we can check)
        # In Flask-WTF, if we run tests without setting WTF_CSRF_ENABLED = False, it may fail. Let's configure it.
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
        if response.status_code == 500:
            print("Response Data (Truncated):", response.data[:2000].decode('utf-8'))
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
