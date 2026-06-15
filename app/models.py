from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import login_manager
from .database import get_document, add_document, get_documents, query_documents, update_document, delete_document

@login_manager.user_loader
def load_user(user_id):
    user_data = get_document('users', user_id)
    if user_data:
        return User(user_data)
    return None

class User(UserMixin):
    def __init__(self, data):
        self.id = data.get('id')
        self.firstname = data.get('firstname', '')
        self.lastname = data.get('lastname', '')
        self.username = data.get('username', '')
        self.email = data.get('email', '')
        self.password_hash = data.get('password_hash', '')
        self.role = data.get('role', 'customer')  # 'customer' or 'admin'
        self.profile_pic_path = data.get('profile_pic_path', '')
        self.created_at = data.get('created_at', '')

    def get_id(self):
        return str(self.id)

    @property
    def is_admin(self):
        return self.role == 'admin'

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def save(self):
        data = {
            'id': self.id,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'role': self.role,
            'profile_pic_path': self.profile_pic_path,
            'created_at': self.created_at
        }
        add_document('users', data, self.id)

    @staticmethod
    def create_user(firstname, lastname, username, email, password, role='customer'):
        password_hash = generate_password_hash(password)
        
        # Check if email or username already exists
        existing_email = query_documents('users', 'email', '==', email)
        if existing_email:
            return None, "Email address already registered"
        
        existing_username = query_documents('users', 'username', '==', username)
        if existing_username:
            return None, "Username already taken"

        user_data = {
            'firstname': firstname,
            'lastname': lastname,
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'role': role,
            'profile_pic_path': '',
        }
        doc_id = add_document('users', user_data)
        user_data['id'] = doc_id
        return User(user_data), None

    @staticmethod
    def get_by_email(email):
        res = query_documents('users', 'email', '==', email)
        if res:
            return User(res[0])
        return None


class Product:
    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name')
        self.category = data.get('category', 'Vegetables')
        self.price = float(data.get('price', 0.0))
        self.unit = data.get('unit', 'per kg')
        self.description = data.get('description', '')
        self.image_url = data.get('image_url', '')
        self.in_stock = data.get('in_stock', True)
        self.created_at = data.get('created_at', '')

    def save(self):
        data = {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'price': self.price,
            'unit': self.unit,
            'description': self.description,
            'image_url': self.image_url,
            'in_stock': self.in_stock,
            'created_at': self.created_at
        }
        add_document('products', data, self.id)

    @staticmethod
    def get_all():
        docs = get_documents('products')
        return [Product(doc) for doc in docs]

    @staticmethod
    def get_by_id(prod_id):
        data = get_document('products', prod_id)
        if data:
            return Product(data)
        return None

    @staticmethod
    def create(name, category, price, unit, description, image_url, in_stock=True):
        data = {
            'name': name,
            'category': category,
            'price': float(price),
            'unit': unit,
            'description': description,
            'image_url': image_url,
            'in_stock': in_stock
        }
        doc_id = add_document('products', data)
        data['id'] = doc_id
        return Product(data)

    @staticmethod
    def delete(prod_id):
        return delete_document('products', prod_id)


class Order:
    def __init__(self, data):
        self.id = data.get('id')
        self.user_id = data.get('user_id')
        self.customer_name = data.get('customer_name')
        self.email = data.get('email')
        self.phone = data.get('phone')
        self.items = data.get('items', [])  # List of maps (product_id, name, price, quantity, image_url)
        self.total_price = float(data.get('total_price', 0.0))
        self.payment_method = data.get('payment_method')  # 'mpesa' | 'paypal' | 'visa'
        self.payment_details = data.get('payment_details', {})  # status, transaction_id, etc.
        self.shipping_address = data.get('shipping_address')
        self.status = data.get('status', 'pending')  # pending, paid, shipped, delivered, cancelled
        self.created_at = data.get('created_at')

    def save(self):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'customer_name': self.customer_name,
            'email': self.email,
            'phone': self.phone,
            'items': self.items,
            'total_price': self.total_price,
            'payment_method': self.payment_method,
            'payment_details': self.payment_details,
            'shipping_address': self.shipping_address,
            'status': self.status,
            'created_at': self.created_at
        }
        add_document('orders', data, self.id)

    @staticmethod
    def get_all():
        docs = get_documents('orders')
        try:
            docs = sorted(docs, key=lambda x: x.get('created_at', ''), reverse=True)
        except Exception:
            pass
        return [Order(doc) for doc in docs]

    @staticmethod
    def get_by_user(user_id):
        res = query_documents('orders', 'user_id', '==', user_id)
        try:
            res = sorted(res, key=lambda x: x.get('created_at', ''), reverse=True)
        except Exception:
            pass
        return [Order(doc) for doc in res]

    @staticmethod
    def get_by_id(order_id):
        data = get_document('orders', order_id)
        if data:
            return Order(data)
        return None

    @staticmethod
    def create(user_id, customer_name, email, phone, items, total_price, payment_method, payment_details, shipping_address, status='pending'):
        data = {
            'user_id': user_id,
            'customer_name': customer_name,
            'email': email,
            'phone': phone,
            'items': items,
            'total_price': float(total_price),
            'payment_method': payment_method,
            'payment_details': payment_details,
            'shipping_address': shipping_address,
            'status': status
        }
        doc_id = add_document('orders', data)
        data['id'] = doc_id
        return Order(data)