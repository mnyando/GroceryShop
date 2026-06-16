import os
from dotenv import load_dotenv
import socket

# Load environment variables from .env file
load_dotenv()

# Set default socket connection timeout to prevent hanging on blocked ports (e.g. SMTP on Render)
socket.setdefaulttimeout(5.0)

class Config:
    '''
    General configuration parent class
    '''
    SECRET_KEY = os.environ.get('SECRET_KEY', 'a-very-secure-secret-key-for-mama-mboga-app-1234')
    
    # Mail configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    
    # Firebase configuration
    FIREBASE_CREDENTIALS_PATH = os.environ.get("FIREBASE_CREDENTIALS_PATH", "serviceAccountKey.json")
    LOCAL_DB_PATH = os.environ.get("LOCAL_DB_PATH", "local_db.json")

    # M-Pesa Daraja Sandbox Configuration
    MPESA_CONSUMER_KEY = os.environ.get("MPESA_CONSUMER_KEY", "OMrHQfEfS09BqYlGCID6iCEPfGRb8G5p9TfYMOqFCRAmMZrz")
    MPESA_CONSUMER_SECRET = os.environ.get("MPESA_CONSUMER_SECRET", "IFVid5KzGOe2AZ3cNspDAhN4H7mHLyAmtfTHNYtv7wrSef8F3WdOQ2vktMsBafKG")
    MPESA_SHORTCODE = os.environ.get("MPESA_SHORTCODE", "174379") # Standard Daraja Sandbox shortcode
    MPESA_PASSKEY = os.environ.get("MPESA_PASSKEY", "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2cbe9") # Standard Daraja Sandbox passkey
    MPESA_CALLBACK_URL = os.environ.get("MPESA_CALLBACK_URL", "https://groceryshop-hjxm.onrender.com/api/payment/mpesa-callback")

class ProdConfig(Config):
    '''
    Production configuration child class
    '''
    DEBUG = False

class DevConfig(Config):
    '''
    Development configuration child class
    '''
    DEBUG = True

config_options = {
    'development': DevConfig,
    'production': ProdConfig,
    'test': DevConfig
}
