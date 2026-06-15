import unittest
import os
import uuid
from app.database import get_document, add_document, delete_document
from app.models import Product, User, Order

class TestDatabaseAndModels(unittest.TestCase):
    
    def setUp(self):
        self.test_ids = []

    def tearDown(self):
        # Cleanup any created test items
        for tid in self.test_ids:
            try:
                delete_document("products", tid)
            except Exception:
                pass
            try:
                delete_document("users", tid)
            except Exception:
                pass
            try:
                delete_document("orders", tid)
            except Exception:
                pass

    def test_product_creation_and_deletion(self):
        """Test creating, reading, and deleting products."""
        # Create product
        prod = Product.create(
            name="Test Vegetable",
            category="Vegetables",
            price=150.0,
            unit="per kg",
            description="Testing product schema details.",
            image_url="http://example.com/test.jpg"
        )
        self.assertIsNotNone(prod.id)
        self.test_ids.append(prod.id)

        # Retrieve and verify
        fetched = Product.get_by_id(prod.id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.name, "Test Vegetable")
        self.assertEqual(fetched.price, 150.0)
        self.assertEqual(fetched.category, "Vegetables")

        # Delete product
        deleted = Product.delete(prod.id)
        self.assertTrue(deleted)

        # Check it is gone
        fetched_after = Product.get_by_id(prod.id)
        self.assertIsNone(fetched_after)

    def test_user_creation_and_validation(self):
        """Test user creation, hashing, and email checks."""
        username = "testuser_" + str(uuid.uuid4().hex[:6])
        email = username + "@example.com"
        
        user, err = User.create_user(
            firstname="Test",
            lastname="User",
            username=username,
            email=email,
            password="securepassword123",
            role="customer"
        )
        self.assertIsNone(err)
        self.assertIsNotNone(user)
        self.test_ids.append(user.id)

        # Test fetching by email
        fetched = User.get_by_email(email)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.username, username)
        
        # Verify password validation
        self.assertTrue(fetched.verify_password("securepassword123"))
        self.assertFalse(fetched.verify_password("wrongpassword"))

    def test_order_creation_flows(self):
        """Test creating e-commerce order transactions."""
        items = [{
            'product_id': 'prod_1',
            'name': 'Fresh Organic Tomatoes',
            'price': 120.0,
            'quantity': 2,
            'image_url': 'http://example.com/tom.jpg'
        }]
        
        order = Order.create(
            user_id="test_user_id",
            customer_name="Test Customer",
            email="customer@example.com",
            phone="0712345678",
            items=items,
            total_price=390.0, # (120*2) + 150 shipping
            payment_method="mpesa",
            payment_details={'status': 'pending', 'transaction_id': 'MPESATESTCODE'},
            shipping_address="Test Address, Nairobi"
        )
        
        self.assertIsNotNone(order.id)
        self.test_ids.append(order.id)

        # Retrieve and verify
        fetched = Order.get_by_id(order.id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.customer_name, "Test Customer")
        self.assertEqual(fetched.total_price, 390.0)
        self.assertEqual(len(fetched.items), 1)
        self.assertEqual(fetched.payment_details['transaction_id'], 'MPESATESTCODE')

if __name__ == '__main__':
    unittest.main()
