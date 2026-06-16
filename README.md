# Mama Mboga | Premium Organic Farm Produce Store

Mama Mboga is a premium, custom e-commerce web application built with Flask and Python, tailored for sourcing fresh organic vegetables and fruits directly from local farms. It features a modern, responsive user experience backed by a flexible hybrid database layer (Firebase Firestore + Local JSON fallback), user authentication, administrative inventory dashboards, and real Safaricom M-Pesa Sandbox STK Push payment integrations.

---

## Key Features

1. **Hybrid Database Adapter**: Uses **Firebase Firestore** in production, but features an automatic **Local JSON Database Fallback** (`local_db.json`) for seamless local development without configuring API credentials.
2. **Modern Glassmorphism Design**: Formatted with Bootstrap 5, Font Awesome, and clean typography, utilizing backdrop blurs, micro-animations, and CSS layout fixes.
3. **Shopping Cart**: Client-side cart persistence synced directly to `localStorage` with a dynamic slide-out cart sidebar.
4. **M-Pesa STK Push Integration**: Lipa Na M-Pesa Online prompt triggered through Safaricom's Daraja Sandbox API, complete with a webhook callback listener that updates order payment status dynamically.
5. **Asynchronous Notification Routing**: System email dispatches are routed through background threads to prevent web requests from hanging on network limits (e.g., SMTP blocks on Render's free tier).
6. **Admin Dashboard**: Control panel for store administrators to monitor revenue, edit product catalogs, and update delivery statuses.

---

## Technical Stack

* **Backend**: Flask (Python 3.10+)
* **Database**: Firebase Admin SDK (Firestore NoSQL) / Local File System Adaptor
* **Frontend UI**: Bootstrap 5, Vanilla CSS, Font Awesome
* **Client Logic**: Vanilla Javascript (Local Storage, Cart State management)
* **Testing**: Python unittest framework
* **Server/Hosting**: Gunicorn, WSGI, Render Ready

---

## Getting Started (Local Development)

### 1. Prerequisites
Ensure you have Python 3.9+ installed on your computer.

### 2. Clone the Repository
```bash
git clone https://github.com/mnyando/GroceryShop.git
cd GroceryShop
```

### 3. Initialize Virtual Environment & Dependencies
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Environment Secrets
Create a `.env` file in the root of the project:
```ini
# Flask Setup
SECRET_KEY=a-very-secure-secret-key-1234
FLASK_CONFIG=development

# M-Pesa Daraja Sandbox Credentials
MPESA_CONSUMER_KEY=OMrHQfEfS09BqYlGCID6iCEPfGRb8G5p9TfYMOqFCRAmMZrz
MPESA_CONSUMER_SECRET=IFVid5KzGOe2AZ3cNspDAhN4H7mHLyAmtfTHNYtv7wrSef8F3WdOQ2vktMsBafKG
MPESA_SHORTCODE=174379
MPESA_PASSKEY=bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2cbe9
MPESA_CALLBACK_URL=https://groceryshop-hjxm.onrender.com/api/payment/mpesa-callback
```

### 5. Running the Application
```bash
python3 wsgi.py
```
The application will boot up on `http://127.0.0.1:5000`.

---

## Configuration & Databases

### Firebase Firestore Setup
To transition the application from the local `local_db.json` offline fallback to a live Firebase Firestore instance:
1. Go to your **[Firebase Console](https://console.firebase.google.com/)** and create a project.
2. Navigate to **Project Settings > Service Accounts**.
3. Generate a new private key and download the credentials JSON.
4. Put the credentials file in your project root and name it **`serviceAccountKey.json`**.
5. The adapter detects this file and switches automatically to Firestore.

*Note: `serviceAccountKey.json` and `.env` are ignored in `.gitignore` to prevent database and credential leaks to GitHub.*

---

## M-Pesa Webhook Callback Handling

The application initiates M-Pesa STK prompts and listens for payments on the `/api/payment/mpesa-callback` route:
* **Immediate Ack**: The server acknowledges Safaricom immediately with an HTTP 200 to prevent retries.
* **Idempotency**: Scans existing logs to verify the transaction `CheckoutRequestID` isn't processed twice.
* **State Sync**: Updates the customer's order to `paid` or `cancelled` depending on the M-Pesa transaction results.

---

## Running Automated Tests

A comprehensive unit testing suite checks authentication logic, phone formatting, M-Pesa sandbox connections, and callback routers.

Run the test suite from the root folder:
```bash
./venv/bin/python3 -m unittest discover -s tests
```

**Output Expected:**
```text
Ran 8 tests in 5.708s
OK
```

---

## MIT License

Copyright (c) 2026 Martin Nyandigisi. Fully licensed under the MIT License guidelines. See `license` file for details.
