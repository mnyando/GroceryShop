import unittest
import os
import json
import uuid
from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.mpesa import format_phone_number, get_mpesa_token
from app.models import Order
from app.database import delete_document
from config import Config

class TestMpesaIntegration(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app('test')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.test_order_ids = []

    def tearDown(self):
        for oid in self.test_order_ids:
            try:
                delete_document('orders', oid)
            except Exception:
                pass
        self.app_context.pop()

    def test_phone_number_formatting(self):
        """Test formatting various phone number formats into 254XXXXXXXXX."""
        self.assertEqual(format_phone_number("0712345678"), "254712345678")
        self.assertEqual(format_phone_number("+254712345678"), "254712345678")
        self.assertEqual(format_phone_number("712345678"), "254712345678")
        self.assertEqual(format_phone_number("0112345678"), "254112345678")
        self.assertEqual(format_phone_number(" 254 712 345 678 "), "254712345678")

    def test_oauth_token_retrieval(self):
        """Test that the provided M-Pesa Sandbox credentials can retrieve an access token."""
        consumer_key = os.environ.get("MPESA_CONSUMER_KEY") or Config.MPESA_CONSUMER_KEY
        consumer_secret = os.environ.get("MPESA_CONSUMER_SECRET") or Config.MPESA_CONSUMER_SECRET
        
        self.assertIsNotNone(consumer_key, "MPESA_CONSUMER_KEY is not set.")
        self.assertIsNotNone(consumer_secret, "MPESA_CONSUMER_SECRET is not set.")
        
        token, err = get_mpesa_token(consumer_key, consumer_secret)
        
        # Verify we got a token and no error
        self.assertIsNone(err, f"Failed to retrieve M-Pesa token: {err}")
        self.assertIsNotNone(token, "Retrieved token is None")
        self.assertTrue(len(token) > 0, "Retrieved token is empty")
        print(f"\n[SUCCESS] Successfully retrieved M-Pesa access token of length {len(token)}!")

    def test_mpesa_callback_success(self):
        """Test callback handling for a successful payment."""
        checkout_id = "TEST_CHECKOUT_" + str(uuid.uuid4().hex[:6]).upper()
        
        # 1. Create a dummy pending order
        order = Order.create(
            user_id="test_customer",
            customer_name="Test Customer",
            email="cust@test.com",
            phone="254712345678",
            items=[],
            total_price=500.0,
            payment_method="mpesa",
            payment_details={"status": "pending", "transaction_id": checkout_id},
            shipping_address="Nairobi"
        )
        self.test_order_ids.append(order.id)
        
        # 2. Simulate Safaricom Callback payload
        payload = {
            "Body": {
                "stkCallback": {
                    "MerchantRequestID": "12345-67890",
                    "CheckoutRequestID": checkout_id,
                    "ResultCode": 0,
                    "ResultDesc": "The service request is processed successfully.",
                    "CallbackMetadata": {
                        "Item": [
                            {"Name": "Amount", "Value": 500.0},
                            {"Name": "MpesaReceiptNumber", "Value": "MPESARECEIPT123"},
                            {"Name": "PhoneNumber", "Value": 254712345678}
                        ]
                    }
                }
            }
        }
        
        # 3. Post to callback endpoint
        response = self.client.post('/api/payment/mpesa-callback', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        # 4. Fetch order and verify it is updated to paid
        updated_order = Order.get_by_id(order.id)
        self.assertEqual(updated_order.status, 'paid')
        self.assertEqual(updated_order.payment_details['status'], 'paid')
        self.assertEqual(updated_order.payment_details['mpesa_receipt'], 'MPESARECEIPT123')

    def test_mpesa_callback_failure(self):
        """Test callback handling for a failed/cancelled payment."""
        checkout_id = "TEST_CHECKOUT_" + str(uuid.uuid4().hex[:6]).upper()
        
        order = Order.create(
            user_id="test_customer",
            customer_name="Test Customer",
            email="cust@test.com",
            phone="254712345678",
            items=[],
            total_price=500.0,
            payment_method="mpesa",
            payment_details={"status": "pending", "transaction_id": checkout_id},
            shipping_address="Nairobi"
        )
        self.test_order_ids.append(order.id)
        
        # ResultCode 1032 means user cancelled the request
        payload = {
            "Body": {
                "stkCallback": {
                    "MerchantRequestID": "12345-67890",
                    "CheckoutRequestID": checkout_id,
                    "ResultCode": 1032,
                    "ResultDesc": "Request cancelled by user."
                }
            }
        }
        
        response = self.client.post('/api/payment/mpesa-callback', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        updated_order = Order.get_by_id(order.id)
        self.assertEqual(updated_order.status, 'cancelled')
        self.assertEqual(updated_order.payment_details['status'], 'failed')
        self.assertEqual(updated_order.payment_details['failure_reason'], 'Request cancelled by user.')

if __name__ == '__main__':
    unittest.main()
