"""
Seed script to populate the database with sample data
Run this after initializing the database
"""

from app import app, db, User, Transaction, bcrypt
from datetime import datetime, timedelta
import random

# Sample data
INCOME_CATEGORIES = ['Salary', 'Freelance', 'Business', 'Investments', 'Gifts', 'Other Income']
EXPENSE_CATEGORIES = ['Food', 'Transport', 'Shopping', 'Bills', 'Entertainment', 'Healthcare', 'Education', 'Other Expense']

SAMPLE_DESCRIPTIONS = {
    'income': [
        'Monthly salary payment',
        'Freelance project completed',
        'Investment dividend',
        'Bonus received',
        'Gift from family',
        'Side project income',
        'Consulting fee',
        'Stock profit'
    ],
    'expense': [
        'Grocery shopping',
        'Gas station',
        'Online shopping',
        'Electricity bill',
        'Movie tickets',
        'Doctor visit',
        'Course enrollment',
        'Restaurant dinner',
        'Coffee shop',
        'Uber ride',
        'Internet bill',
        'Gym membership'
    ]
}

def create_sample_user():
    """Create a sample user for testing"""
    # Check if demo user exists
    demo_user = User.query.filter_by(email='demo@financetracker.com').first()
    
    if demo_user:
        print("Demo user already exists!")
        return demo_user
    
    # Create demo user
    hashed_password = bcrypt.generate_password_hash('demo123').decode('utf-8')
    demo_user = User(
        name='Demo User',
        email='demo@financetracker.com',
        password=hashed_password
    )
    
    db.session.add(demo_user)
    db.session.commit()
    
    print(f"✅ Created demo user: demo@financetracker.com / demo123")
    return demo_user

def create_sample_transactions(user_id, num_transactions=50):
    """Create sample transactions for the last 6 months"""
    transactions = []
    current_date = datetime.now()
    
    print(f"\n📊 Creating {num_transactions} sample transactions...")
    
    for i in range(num_transactions):
        # Random date within last 6 months
        days_ago = random.randint(0, 180)
        transaction_date = current_date - timedelta(days=days_ago)
        
        # Random transaction type (60% expense, 40% income)
        transaction_type = 'expense' if random.random() < 0.6 else 'income'
        
        # Select category and description
        if transaction_type == 'income':
            category = random.choice(INCOME_CATEGORIES)
            description = random.choice(SAMPLE_DESCRIPTIONS['income'])
            amount = random.uniform(500, 5000)  # Income amounts
        else:
            category = random.choice(EXPENSE_CATEGORIES)
            description = random.choice(SAMPLE_DESCRIPTIONS['expense'])
            amount = random.uniform(10, 500)  # Expense amounts
        
        transaction = Transaction(
            user_id=user_id,
            type=transaction_type,
            category=category,
            amount=round(amount, 2),
            description=description,
            date=transaction_date
        )
        
        transactions.append(transaction)
    
    # Add all transactions to database
    db.session.bulk_save_objects(transactions)
    db.session.commit()
    
    print(f"✅ Created {num_transactions} transactions successfully!")
    
    # Calculate summary
    income_total = sum(t.amount for t in transactions if t.type == 'income')
    expense_total = sum(t.amount for t in transactions if t.type == 'expense')
    balance = income_total - expense_total
    
    print(f"\n💰 Summary:")
    print(f"   Total Income: ${income_total:,.2f}")
    print(f"   Total Expenses: ${expense_total:,.2f}")
    print(f"   Balance: ${balance:,.2f}")

def seed_database():
    """Main function to seed the database"""
    with app.app_context():
        print("🌱 Starting database seeding...")
        
        # Create tables if they don't exist
        db.create_all()
        print("✅ Database tables created/verified")
        
        # Create demo user
        demo_user = create_sample_user()
        
        # Create sample transactions
        create_sample_transactions(demo_user.id, num_transactions=50)
        
        print("\n✨ Database seeding completed!")
        print("\n🔑 Login credentials:")
        print("   Email: demo@financetracker.com")
        print("   Password: demo123")
        print("\n🚀 Start the application with: python app.py")

if __name__ == '__main__':
    seed_database()