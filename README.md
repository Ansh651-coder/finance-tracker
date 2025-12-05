# 💰 Personal Finance Tracker

A full-stack web application for managing personal finances with user authentication, transaction management, analytics, and data export features.

![Finance Tracker](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

### 🔐 Authentication
- User registration and login
- JWT-based authentication
- Secure password hashing with bcrypt
- Protected API routes

### 💸 Transaction Management
- Add, edit, and delete transactions
- Support for both income and expense
- Categories for better organization
- Date-based tracking
- Detailed descriptions

### 📊 Dashboard & Analytics
- Real-time financial summary
- Total income, expenses, and balance
- Interactive charts:
  - Income vs Expense bar chart
  - Category breakdown pie chart
  - Monthly trend line chart
- Category-wise spending analysis

### 📤 Data Export
- Export transactions to Excel (XLSX)
- Export to PDF with summary
- Complete transaction history

### 👤 User Profile
- Update personal information
- Change password
- Account statistics
- Profile management

### 📱 Responsive Design
- Mobile-first approach
- Modern UI with Tailwind CSS
- Smooth animations
- Intuitive navigation

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- Docker (optional, for containerized deployment)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd finance-tracker
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and update SECRET_KEY and other configurations
```

5. **Initialize the database**
```bash
python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

6. **Run the application**
```bash
python app.py
```

Visit `http://localhost:5000` in your browser.

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

1. **Build and run with Docker Compose**
```bash
docker-compose up -d
```

2. **Access the application**
- Application: `http://localhost:5000`
- PostgreSQL: `localhost:5432` (if using PostgreSQL service)

3. **Stop the application**
```bash
docker-compose down
```

### Using Docker Only

1. **Build the image**
```bash
docker build -t finance-tracker .
```

2. **Run the container**
```bash
docker run -d -p 5000:5000 \
  -e SECRET_KEY=your-secret-key \
  -e DATABASE_URL=sqlite:///finance_tracker.db \
  --name finance-tracker \
  finance-tracker
```

## 🌐 Deployment on Render

### Step 1: Prepare Your Repository
1. Push your code to GitHub
2. Ensure all files are committed

### Step 2: Deploy on Render

1. **Create a new Web Service on Render**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure the service**
   - **Name**: finance-tracker
   - **Environment**: Docker
   - **Region**: Choose closest to your users
   - **Branch**: main

3. **Environment Variables**
   Add these in the Render dashboard:
   ```
   SECRET_KEY=<generate-a-strong-secret-key>
   DATABASE_URL=<render-will-provide-if-using-postgres>
   FLASK_ENV=production
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy

### Step 3: Database Setup (Optional - PostgreSQL)

1. **Create a PostgreSQL database**
   - In Render dashboard, create a new PostgreSQL database
   - Copy the Internal Database URL

2. **Update DATABASE_URL**
   - Add the PostgreSQL URL to your web service environment variables

3. **Initialize database**
   - Use Render's shell to run database migrations

## 📁 Project Structure

```
finance-tracker/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose configuration
├── .env.example          # Environment variables template
├── README.md             # Project documentation
├── templates/            # HTML templates
│   ├── index.html       # Login/Register page
│   ├── dashboard.html   # Main dashboard
│   ├── transactions.html # Transaction management
│   └── profile.html     # User profile
└── static/              # Static files
    └── uploads/         # User uploaded files
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Secret key for JWT encoding | `dev-secret-key-change-in-production` |
| `DATABASE_URL` | Database connection string | `sqlite:///finance_tracker.db` |
| `FLASK_ENV` | Environment (development/production) | `production` |
| `PORT` | Application port | `5000` |

### Database Options

**SQLite (Default)**
```
DATABASE_URL=sqlite:///finance_tracker.db
```

**PostgreSQL**
```
DATABASE_URL=postgresql://user:password@host:port/database
```

## 🎨 Customization

### Categories

Edit the categories in the JavaScript files:

```javascript
const INCOME_CATEGORIES = ['Salary', 'Freelance', 'Business', 'Investments', 'Gifts', 'Other'];
const EXPENSE_CATEGORIES = ['Food', 'Transport', 'Shopping', 'Bills', 'Entertainment', 'Healthcare'];
```

### Theme Colors

Modify the gradient colors in the templates:

```css
.gradient-bg {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
```

## 🔒 Security Features

- Password hashing with bcrypt
- JWT token-based authentication
- Protected API routes
- SQL injection prevention with SQLAlchemy ORM
- CORS configuration
- Input validation
- XSS protection

## 📊 API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user

### Transactions
- `GET /transactions` - Get all transactions
- `POST /transactions` - Create transaction
- `GET /transactions/:id` - Get specific transaction
- `PUT /transactions/:id` - Update transaction
- `DELETE /transactions/:id` - Delete transaction

### Analytics
- `GET /summary` - Get financial summary

### Export
- `GET /export/excel` - Export to Excel
- `GET /export/pdf` - Export to PDF

### Profile
- `PUT /profile` - Update user profile

## 🧪 Testing

### Manual Testing

1. **Register a new user**
   - Navigate to `/`
   - Click "Sign Up"
   - Fill in details and register

2. **Add transactions**
   - Go to dashboard
   - Click "Add Income" or "Add Expense"
   - Fill in transaction details

3. **View analytics**
   - Check dashboard for charts
   - View category breakdown

4. **Export data**
   - Click "Export Excel" or "Export PDF"
   - Download and verify files

## 🐛 Troubleshooting

### Database Issues

**SQLite database locked**
```bash
# Stop all running instances
# Delete finance_tracker.db
# Reinitialize database
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### Docker Issues

**Port already in use**
```bash
# Change port in docker-compose.yml
ports:
  - "5001:5000"  # Change 5001 to any available port
```

### Import Errors

**Missing dependencies**
```bash
pip install -r requirements.txt --upgrade
```

## 📝 License

This project is licensed under the MIT License.

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions, please open an issue on GitHub.

## 🙏 Acknowledgments

- Flask framework
- Chart.js for beautiful charts
- Tailwind CSS for styling
- ReportLab for PDF generation
- All open-source contributors

---

Made with ❤️ for better financial management