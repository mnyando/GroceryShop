from threading import Thread
from flask_mail import Message
from flask import render_template, current_app
from . import mail

def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            print(f"[MAIL ERROR] Async email send failed: {e}")

def mail_message(subject, template, to, **kwargs):
    sender_email = 'cheruden25@gmail.com'

    email = Message(subject, sender=sender_email, recipients=[to])
    email.body = render_template(template + ".txt", **kwargs)
    email.html = render_template(template + ".html", **kwargs)
    
    # Retrieve the true Flask app instance
    app = current_app._get_current_object()
    
    # Dispatch sending to a background thread
    thr = Thread(target=send_async_email, args=[app, email])
    thr.start()
    return thr
