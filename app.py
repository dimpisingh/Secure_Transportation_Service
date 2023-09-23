# Import necessary libraries
from flask_mail import Mail, Message
from flask import Flask, request, jsonify, session, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer  # Library for token generation
import os


# Initialize the Flask application
app = Flask(__name__)

 # Generate a random secret key
secret_key = os.urandom(24)
app.secret_key = secret_key

# Configure the PostgreSQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://dimpisingh:7@SureshSingh@localhost/ridesharing'
db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)

# Initialize the Flask-Mail extension
app.config['MAIL_SERVER'] = 'smtp.example.com'  # Replace with your email provider's SMTP server
app.config['MAIL_PORT'] = 587  # Replace with the appropriate port
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@example.com'  # Replace with your email address
app.config['MAIL_PASSWORD'] = 'your_email_password'  # Replace with your email password

mail = Mail(app)

# Initialize the token serializer
token_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# Route for user registration
@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        # Get user input from the registration form
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Hash the password before storing it in the database
        password_hash = generate_password_hash(password, method='sha256')

        # Create a new user instance and add it to the database
        new_user = User(username=username, email=email, password_hash=password_hash, is_verified=False)
        db.session.add(new_user)
        db.session.commit()

        # Generate an email verification token
        token = token_serializer.dumps(email, salt='email-verification')

        # Send the verification email
        verification_link = url_for('verify_email', token=token, _external=True)
        subject = 'Email Verification'
        message = f'Click the following link to verify your email address: {verification_link}'
        send_email(email, subject, message)

        return jsonify({'message': 'User registered successfully. Please check your email for verification instructions.'})

# Route for email verification
@app.route('/verify_email/<token>')
def verify_email(token):
    try:
        email = token_serializer.loads(token, salt='email-verification', max_age=3600)  # Token expires in 1 hour
        user = User.query.filter_by(email=email).first()

        if user:
            # Mark the user as verified
            user.is_verified = True
            db.session.commit()
            return jsonify({'message': 'Email verification successful. You can now log in.'})
        else:
            return jsonify({'error': 'Invalid email verification token.'})
    except Exception as e:
        return jsonify({'error': str(e)})

# Route for user login
@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        # Get user input from the login form
        username = request.form['username']
        password = request.form['password']

        # Query the database to find the user by username
        user = User.query.filter_by(username=username).first()

        # Check if the user exists and the password is correct
        if user and check_password_hash(user.password_hash, password):
            # Store user information in the session
            session['user_id'] = user.id
            return jsonify({'message': 'Login successful'})
        else:
            return jsonify({'error': 'Invalid username or password'})

# Route to check if the user is logged in
@app.route('/check_login')
def check_login():
    if 'user_id' in session:
        return jsonify({'message': 'User is logged in'})
    else:
        return jsonify({'error': 'User is not logged in'})

# Function to send email
def send_email(to, subject, message):
    msg = Message(subject, sender='dimpisingh59@gmail.com', recipients=[to])
    msg.body = message
    mail.send(msg)

# Middleware to check email verification before accessing certain routes
@app.before_request
def check_email_verification():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if not user.is_verified:
            # Redirect the user to the email verification page or display a message
            return render_template('email_verification_required.html')

# Route to initiate email verification
@app.route('/verify_email')
def initiate_email_verification():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if not user.is_verified:
            # Generate a new email verification token and send the verification email (as described in the previous response)
            
            # ...
            return render_template('email_verification_sent.html')
    return redirect(url_for('index'))  # Redirect to the home page if not logged in or already verified

# Sample restricted page protected by email verification
@app.route('/restricted_page')
def restricted_page():
    # This route is protected by the email verification check middleware
    return render_template('restricted_page.html')

if __name__ == '__main__':   
    app.run(debug=True)
