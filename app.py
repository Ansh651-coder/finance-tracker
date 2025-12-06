"""
Personal Finance Tracker - Flask Application
Main application file with all routes and configuration
"""

from flask import Flask, render_template, request, jsonify, send_file, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from functools import wraps
import jwt
import os
from io import BytesIO
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import json

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///finance_tracker.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
CORS(app)
# Auto-create all tables on startup (works on Render)
with app.app_context():
    try:
        db.create_all()
        print("✔ Database tables initialized")
    except Exception as e:
        print("❌ Error initializing database:", e)


# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ==================== MODELS ====================

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    profile_picture = db.Column(db.String(255), default='default.png')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    transactions = db.relationship('Transaction', backref='user', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'profile_picture': self.profile_picture,
            'created_at': self.created_at.isoformat()
        }

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'income' or 'expense'
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'category': self.category,
            'amount': self.amount,
            'description': self.description,
            'date': self.date.isoformat(),
            'created_at': self.created_at.isoformat()
        }

# ==================== JWT HELPERS ====================

def generate_token(user_id):
    """Generate JWT token for user"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def token_required(f):
    """Decorator to protect routes with JWT"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            token = request.cookies.get('token')
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        if token.startswith('Bearer '):
            token = token.split(' ')[1]
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

# ==================== AUTH ROUTES ====================

@app.route('/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    # Validate input
    if not data or not data.get('name') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if user exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Hash password
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    
    # Create user
    new_user = User(
        name=data['name'],
        email=data['email'],
        password=hashed_password
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    # Generate token
    token = generate_token(new_user.id)
    
    return jsonify({
        'message': 'User registered successfully',
        'token': token,
        'user': new_user.to_dict()
    }), 201

@app.route('/auth/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing email or password'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not bcrypt.check_password_hash(user.password, data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    token = generate_token(user.id)
    
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': user.to_dict()
    }), 200

@app.route('/auth/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """Get current user info"""
    return jsonify({'user': current_user.to_dict()}), 200

# ==================== TRANSACTION ROUTES ====================

@app.route('/transactions', methods=['GET'])
@token_required
def get_transactions(current_user):
    """Get all transactions for current user"""
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()
    return jsonify({'transactions': [t.to_dict() for t in transactions]}), 200

@app.route('/transactions', methods=['POST'])
@token_required
def create_transaction(current_user):
    """Create a new transaction"""
    data = request.get_json()
    
    # Validate input
    required_fields = ['type', 'category', 'amount', 'date']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if data['type'] not in ['income', 'expense']:
        return jsonify({'error': 'Type must be income or expense'}), 400
    
    try:
        amount = float(data['amount'])
        if amount <= 0:
            return jsonify({'error': 'Amount must be positive'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid amount'}), 400
    
    # Parse date
    try:
        transaction_date = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
    except:
        return jsonify({'error': 'Invalid date format'}), 400
    
    # Create transaction
    new_transaction = Transaction(
        user_id=current_user.id,
        type=data['type'],
        category=data['category'],
        amount=amount,
        description=data.get('description', ''),
        date=transaction_date
    )
    
    db.session.add(new_transaction)
    db.session.commit()
    
    return jsonify({
        'message': 'Transaction created successfully',
        'transaction': new_transaction.to_dict()
    }), 201

@app.route('/transactions/<int:transaction_id>', methods=['GET'])
@token_required
def get_transaction(current_user, transaction_id):
    """Get a specific transaction"""
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first()
    
    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404
    
    return jsonify({'transaction': transaction.to_dict()}), 200

@app.route('/transactions/<int:transaction_id>', methods=['PUT'])
@token_required
def update_transaction(current_user, transaction_id):
    """Update a transaction"""
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first()
    
    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404
    
    data = request.get_json()
    
    # Update fields
    if 'type' in data:
        if data['type'] not in ['income', 'expense']:
            return jsonify({'error': 'Type must be income or expense'}), 400
        transaction.type = data['type']
    
    if 'category' in data:
        transaction.category = data['category']
    
    if 'amount' in data:
        try:
            amount = float(data['amount'])
            if amount <= 0:
                return jsonify({'error': 'Amount must be positive'}), 400
            transaction.amount = amount
        except ValueError:
            return jsonify({'error': 'Invalid amount'}), 400
    
    if 'description' in data:
        transaction.description = data['description']
    
    if 'date' in data:
        try:
            transaction.date = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
        except:
            return jsonify({'error': 'Invalid date format'}), 400
    
    db.session.commit()
    
    return jsonify({
        'message': 'Transaction updated successfully',
        'transaction': transaction.to_dict()
    }), 200

@app.route('/transactions/<int:transaction_id>', methods=['DELETE'])
@token_required
def delete_transaction(current_user, transaction_id):
    """Delete a transaction"""
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first()
    
    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404
    
    db.session.delete(transaction)
    db.session.commit()
    
    return jsonify({'message': 'Transaction deleted successfully'}), 200

# ==================== SUMMARY/ANALYTICS ROUTES ====================

@app.route('/summary', methods=['GET'])
@token_required
def get_summary(current_user):
    """Get financial summary and analytics"""
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    
    total_income = sum(t.amount for t in transactions if t.type == 'income')
    total_expense = sum(t.amount for t in transactions if t.type == 'expense')
    balance = total_income - total_expense
    
    # Category-wise spending
    category_spending = {}
    for t in transactions:
        if t.type == 'expense':
            category_spending[t.category] = category_spending.get(t.category, 0) + t.amount
    
    # Monthly summary (last 12 months)
    monthly_data = {}
    for t in transactions:
        month_key = t.date.strftime('%Y-%m')
        if month_key not in monthly_data:
            monthly_data[month_key] = {'income': 0, 'expense': 0}
        
        if t.type == 'income':
            monthly_data[month_key]['income'] += t.amount
        else:
            monthly_data[month_key]['expense'] += t.amount
    
    # Sort monthly data
    sorted_months = sorted(monthly_data.keys())[-12:]
    monthly_summary = [
        {
            'month': month,
            'income': monthly_data[month]['income'],
            'expense': monthly_data[month]['expense']
        }
        for month in sorted_months
    ]
    
    return jsonify({
        'total_income': round(total_income, 2),
        'total_expense': round(total_expense, 2),
        'balance': round(balance, 2),
        'category_spending': category_spending,
        'monthly_summary': monthly_summary,
        'transaction_count': len(transactions)
    }), 200

# ==================== EXPORT ROUTES ====================

@app.route('/export/excel', methods=['GET'])
@token_required
def export_excel(current_user):
    """Export transactions as Excel file"""
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()
    
    # Prepare data
    data = []
    for t in transactions:
        data.append({
            'Date': t.date.strftime('%Y-%m-%d'),
            'Type': t.type.capitalize(),
            'Category': t.category,
            'Amount': t.amount,
            'Description': t.description
        })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Create Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Transactions', index=False)
        
        # Add summary sheet
        summary_data = {
            'Metric': ['Total Income', 'Total Expense', 'Balance'],
            'Value': [
                sum(t.amount for t in transactions if t.type == 'income'),
                sum(t.amount for t in transactions if t.type == 'expense'),
                sum(t.amount for t in transactions if t.type == 'income') - 
                sum(t.amount for t in transactions if t.type == 'expense')
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
    
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'transactions_{datetime.now().strftime("%Y%m%d")}.xlsx'
    )

@app.route('/export/pdf', methods=['GET'])
@token_required
def export_pdf(current_user):
    """Export transactions as PDF file"""
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()
    
    # Create PDF in memory
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    
    # Title
    title = Paragraph(f"Transaction Report - {current_user.name}", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.3*inch))
    
    # Summary
    total_income = sum(t.amount for t in transactions if t.type == 'income')
    total_expense = sum(t.amount for t in transactions if t.type == 'expense')
    balance = total_income - total_expense
    
    summary_text = f"""
    <b>Summary:</b><br/>
    Total Income: ${total_income:,.2f}<br/>
    Total Expense: ${total_expense:,.2f}<br/>
    Balance: ${balance:,.2f}<br/>
    Report Date: {datetime.now().strftime('%Y-%m-%d')}
    """
    summary = Paragraph(summary_text, styles['Normal'])
    elements.append(summary)
    elements.append(Spacer(1, 0.3*inch))
    
    # Transactions table
    data = [['Date', 'Type', 'Category', 'Amount', 'Description']]
    for t in transactions:
        data.append([
            t.date.strftime('%Y-%m-%d'),
            t.type.capitalize(),
            t.category,
            f"${t.amount:,.2f}",
            t.description[:30] + '...' if len(t.description) > 30 else t.description
        ])
    
    table = Table(data, colWidths=[1.2*inch, 1*inch, 1.2*inch, 1.2*inch, 2.4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    
    doc.build(elements)
    buffer.seek(0)
    
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'transactions_{datetime.now().strftime("%Y%m%d")}.pdf'
    )

# ==================== PROFILE ROUTES ====================

@app.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """Update user profile"""
    data = request.get_json()
    
    if 'name' in data:
        current_user.name = data['name']
    
    if 'email' in data:
        # Check if email is already taken
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.id != current_user.id:
            return jsonify({'error': 'Email already in use'}), 400
        current_user.email = data['email']
    
    if 'password' in data and data['password']:
        current_user.password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    
    db.session.commit()
    
    return jsonify({
        'message': 'Profile updated successfully',
        'user': current_user.to_dict()
    }), 200

# ==================== FRONTEND ROUTES ====================

@app.route('/')
def index():
    """Home page - redirect to login"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard page"""
    return render_template('dashboard.html')

@app.route('/transactions-page')
def transactions_page():
    """Transactions page"""
    return render_template('transactions.html')

@app.route('/profile-page')
def profile_page():
    """Profile page"""
    return render_template('profile.html')

# ==================== INITIALIZE DATABASE ====================

def init_db():
    """Initialize database and create tables"""
    with app.app_context():
        db.create_all()
        print("Database initialized successfully!")

# ==================== RUN APPLICATION ====================

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)