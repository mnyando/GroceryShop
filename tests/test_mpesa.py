import unittest
import os
from dotenv import load_dotenv
load_dotenv()

from app.mpesa import format_phone_number, get_mpesa_token
from config import Config

class TestMpesaIntegration(unittest.TestCase):
    
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

if __name__ == '__main__':
    unittest.main()
