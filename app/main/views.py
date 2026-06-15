from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from . import main
from ..models import Product, Order, User
from functools import wraps
import datetime
import uuid
import time

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Access denied. Admin privileges required.")
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@main.route('/')
def index():
    products = Product.get_all()
    # Unique categories for filtering
    categories = sorted(list(set([p.category for p in products])))
    return render_template('index.html', products=products, categories=categories)

@main.route('/checkout')
def checkout():
    # If not logged in, they can still access checkout but we encourage authentication
    products = Product.get_all()
    return render_template('checkout.html', products=products)

@main.route('/cart')
def cart():
    # Simply renders a dedicated cart page if needed, but we also support slide-out modal cart
    return render_template('cart.html')

# Payment and Order API endpoints

@main.route('/api/payment/stk-push', methods=['POST'])
def mpesa_stk_push():
    data = request.get_json() or {}
    phone = data.get('phone')
    amount = data.get('amount')
    
    if not phone or not amount:
        return jsonify({'success': False, 'message': 'Phone and amount are required.'}), 400
    
    # Mocking STK Push API call
    # In a real environment, you make a POST request to Safaricom Daraja API
    # Here we simulate the network trigger and returns immediate response
    transaction_id = "MPESA" + str(uuid.uuid4().hex[:8]).upper()
    return jsonify({
        'success': True,
        'message': f'STK push notification sent to {phone}. Check your phone to enter M-Pesa PIN.',
        'transaction_id': transaction_id,
        'timestamp': datetime.datetime.now().isoformat()
    })

@main.route('/api/order/create', methods=['POST'])
def create_order():
    data = request.get_json() or {}
    shipping = data.get('shipping', {})
    cart_items = data.get('items', [])
    payment_method = data.get('payment_method')
    payment_details = data.get('payment_details', {})
    
    if not cart_items:
        return jsonify({'success': False, 'message': 'Your cart is empty.'}), 400
        
    if not shipping.get('address') or not shipping.get('phone') or not shipping.get('name'):
        return jsonify({'success': False, 'message': 'Shipping details (name, phone, address) are required.'}), 400

    # Calculate and validate price on backend to prevent client-side hacks
    total_price = 0.0
    verified_items = []
    
    for item in cart_items:
        product = Product.get_by_id(item.get('id'))
        if not product:
            return jsonify({'success': False, 'message': f"Product {item.get('name')} not found."}), 400
        
        qty = int(item.get('quantity', 1))
        item_total = product.price * qty
        total_price += item_total
        
        verified_items.append({
            'product_id': product.id,
            'name': product.name,
            'price': product.price,
            'quantity': qty,
            'image_url': product.image_url
        })
        
    # Standard shipping fee
    shipping_fee = 150.0
    grand_total = total_price + shipping_fee
    
    # Authenticated user ID or guest checkout
    user_id = current_user.id if current_user.is_authenticated else "guest_" + str(uuid.uuid4().hex[:6])
    email = current_user.email if current_user.is_authenticated else shipping.get('email', 'guest@mamamboga.com')
    
    # Create the order
    order = Order.create(
        user_id=user_id,
        customer_name=shipping.get('name'),
        email=email,
        phone=shipping.get('phone'),
        items=verified_items,
        total_price=grand_total,
        payment_method=payment_method,
        payment_details={
            'status': 'paid' if payment_method in ['paypal', 'visa'] or payment_details.get('transaction_id') else 'pending',
            'transaction_id': payment_details.get('transaction_id', 'CASH_' + str(uuid.uuid4().hex[:8]).upper()),
            'paybill': payment_details.get('paybill', ''),
            'account_number': payment_details.get('account_number', '')
        },
        shipping_address=shipping.get('address'),
        status='paid' if payment_method in ['paypal', 'visa'] else 'pending'
    )
    
    return jsonify({
        'success': True,
        'message': 'Order placed successfully!',
        'order_id': order.id
    })

# Admin dashboard routes

@main.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    orders = Order.get_all()
    products = Product.get_all()
    
    # Calculate simple stats
    revenue = sum([order.total_price for order in orders if order.status in ['paid', 'shipped', 'delivered']])
    pending_orders = len([o for o in orders if o.status == 'pending'])
    total_sales_count = len([o for o in orders if o.status in ['paid', 'shipped', 'delivered']])
    
    return render_template(
        'admin/dashboard.html', 
        orders=orders, 
        products=products,
        revenue=revenue,
        pending_orders=pending_orders,
        total_sales_count=total_sales_count
    )

@main.route('/admin/product/add', methods=['POST'])
@login_required
@admin_required
def admin_add_product():
    name = request.form.get('name')
    category = request.form.get('category')
    price = request.form.get('price')
    unit = request.form.get('unit')
    description = request.form.get('description')
    image_url = request.form.get('image_url')
    
    if not name or not price:
        flash("Product name and price are required.")
        return redirect(url_for('main.admin_dashboard'))
        
    # Default placeholder image if none provided
    if not image_url:
        image_url = "https://images.pexels.com/photos/1132047/pexels-photo-1132047.jpeg?auto=compress&cs=tinysrgb&w=800"

    Product.create(
        name=name,
        category=category,
        price=price,
        unit=unit,
        description=description,
        image_url=image_url
    )
    flash(f"Product '{name}' added successfully!")
    return redirect(url_for('main.admin_dashboard'))

@main.route('/admin/product/delete/<string:prod_id>', methods=['POST', 'GET'])
@login_required
@admin_required
def admin_delete_product(prod_id):
    product = Product.get_by_id(prod_id)
    if product:
        Product.delete(prod_id)
        flash(f"Product '{product.name}' deleted successfully.")
    else:
        flash("Product not found.")
    return redirect(url_for('main.admin_dashboard'))

@main.route('/admin/order/status/<string:order_id>', methods=['POST'])
@login_required
@admin_required
def admin_update_order_status(order_id):
    status = request.form.get('status')
    order = Order.get_by_id(order_id)
    if order and status:
        order.status = status
        # If order status becomes delivered/shipped, mark payment as paid as well
        if status in ['shipped', 'delivered']:
            order.payment_details['status'] = 'paid'
        order.save()
        flash(f"Order status updated to '{status}'.")
    else:
        flash("Order not found or invalid status.")
    return redirect(url_for('main.admin_dashboard'))

@main.route('/profile/<string:uname>')
@login_required
def user_profile(uname):
    from ..database import query_documents
    users = query_documents('users', 'username', '==', uname)
    if not users:
        abort(404)
    user = User(users[0])
    
    # Check authorization (only user themselves or admin can view profile)
    if current_user.id != user.id and not current_user.is_admin:
        abort(403)
        
    orders = Order.get_by_user(user.id)
    return render_template('profile/profile.html', user=user, orders=orders)
