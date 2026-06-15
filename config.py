import os

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
