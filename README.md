<p align="center">
  <img src="https://img.shields.io/badge/Django-4.2-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/TailwindCSS-3.x-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white" alt="TailwindCSS">
  <img src="https://img.shields.io/badge/DaisyUI-4.x-5A0EF8?style=for-the-badge&logo=daisyui&logoColor=white" alt="DaisyUI">
  <img src="https://img.shields.io/badge/Gemini_AI-Powered-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Gemini AI">
</p>

# 📦 Inventory Pro - نظام إدارة المخزون

<p align="center">
  <strong>A comprehensive, AI-powered inventory management system built with Django</strong>
  <br>
  <em>نظام متكامل لإدارة المخزون والمبيعات مدعوم بالذكاء الاصطناعي</em>
</p>

---

## 🎬 Demo

<!-- VIDEO_PLACEHOLDER: Add your demo video URL here -->
[![Demo Video](https://img.shields.io/badge/▶_Watch_Demo-Video-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://youtu.be/m-t_s0jpSo8)

![Demo Video](https://github.com/M-Alhbyb/Django_Inventory_System/blob/master/demo/demo.gif)

---

## ✨ Features

### 📊 Dashboard & Analytics
- **Real-time Statistics** – Overview of products, categories, merchants, and representatives
- **Transaction History** – Paginated list of recent transactions with filtering
- **Quick Actions** – Fast access to common operations directly from the dashboard

### 📦 Inventory Management
- **Product Catalog** – Full CRUD operations for products with category organization
- **Category Management** – Organize products into logical categories
- **Stock Tracking** – Real-time stock levels with low-stock alerts
- **Stock Prediction** – AI-powered stock depletion forecasting using Prophet time series analysis

### 👥 Partner Management
- **Merchants (التجار)** – Track merchant debt, transactions, and payment history
- **Representatives (المندوبين)** – Manage product distribution and returns
- **Detailed Profiles** – View complete transaction history per partner

### 💰 Transaction System
- **Take (أخذ)** – Record product withdrawals from inventory
- **Payment (دفع)** – Track merchant payments to reduce debt
- **Restore (إرجاع)** – Handle product returns to inventory
- **Fees (منصرف)** – Log miscellaneous expenses

### 📈 Comprehensive Reports
- **Date-range Filtering** – Generate reports for any time period
- **Top Merchants** – Identify highest-value merchants
- **Top Products** – Track best-selling products
- **Category Performance** – Analyze sales by category
- **Daily Trends** – Visualize transaction patterns
- **Individual Reports** – Detailed merchant and product reports

### 🤖 AI-Powered Chat Assistant
- **20+ AI Tools** – Comprehensive function calling capabilities
- **Natural Language Queries** – Ask questions in Arabic about your inventory
- **Real-time Data Access** – AI can query products, transactions, users, and more
- **Smart Analytics** – Get insights, predictions, and alerts through conversation
- **Markdown Support** – Beautifully formatted AI responses

### 📥 Import/Export
- **Excel Export** – Export transactions with full styling and RTL support
- **Data Import** – Import transactions from Excel files using django-import-export
- **Arabic Headers** – Properly localized column names

### 🎨 Modern UI/UX
- **Arabic RTL Support** – Full right-to-left layout optimization
- **Light Theme** – Clean, modern light-colored interface
- **Collapsible Sidebar** – Save screen space with icon-only mode
- **Responsive Design** – Works on desktop and mobile devices
- **Glassmorphism Effects** – Modern visual styling
- **Smooth Animations** – Micro-interactions for better UX

---

## 🛠️ Tech Stack

| Component         | Technology                                          |
| ----------------- | --------------------------------------------------- |
| **Backend**       | Django 4.2, Python 3.10+                            |
| **Frontend**      | TailwindCSS 3.x, DaisyUI 4.x                        |
| **Database**      | SQLite (development), PostgreSQL (production-ready) |
| **AI/ML**         | Google Gemini 2.5 Flash, Prophet (time series)      |
| **Task Queue**    | Celery + Redis                                      |
| **Icons**         | Font Awesome 6                                      |
| **Fonts**         | Cairo (Arabic), Inter (System)                      |
| **Import/Export** | django-import-export, openpyxl                      |

---

## 📁 Project Structure

```
inventory/
├── base/                          # Main application
│   ├── management/commands/       # Custom Django commands
│   │   └── populate_data.py       # Faker data generator
│   ├── migrations/                # Database migrations
│   ├── static/                    # App-specific static files
│   ├── templates/                 # HTML templates
│   │   ├── ai.html                # AI assistant page
│   │   ├── categories.html        # Category management
│   │   ├── dashboard.html         # Main dashboard
│   │   ├── inventory.html         # Inventory view
│   │   ├── partners/              # Partner templates
│   │   ├── products.html          # Product management
│   │   ├── reports.html           # Reports dashboard
│   │   └── transactions.html      # Transaction management
│   ├── views/                     # View modules
│   │   ├── ai.py                  # AI-related views
│   │   ├── categories.py          # Category CRUD
│   │   ├── fees.py                # Fees handling
│   │   ├── general.py             # Dashboard
│   │   ├── inventory.py           # Inventory views
│   │   ├── partners.py            # Partner management
│   │   ├── products.py            # Product CRUD
│   │   ├── reports.py             # Report generation
│   │   └── transactions.py        # Transaction handling
│   ├── models.py                  # Data models
│   ├── forms.py                   # Django forms
│   ├── resources.py               # Import/Export resources
│   ├── tasks.py                   # Celery tasks
│   └── urls.py                    # URL routing
├── chat/                          # AI Chat application
│   ├── services.py                # Gemini AI integration
│   ├── tools.py                   # 20+ AI function tools
│   ├── views.py                   # Chat API endpoints
│   └── templates/                 # Chat templates
├── inventory/                     # Project configuration
│   ├── settings.py                # Django settings
│   ├── urls.py                    # Root URL config
│   ├── celery.py                  # Celery configuration
│   └── wsgi.py                    # WSGI entry point
├── static/                        # Global static files
│   ├── css/                       # Custom stylesheets
│   └── vendor/                    # Third-party assets
├── templates/                     # Global templates
│   ├── base.html                  # Base template
│   └── partials/                  # Reusable components
│       ├── sidebar.html           # Navigation sidebar
│       └── chat_widget.html       # Floating chat widget
└── manage.py                      # Django CLI
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- Redis (for Celery)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/inventory-pro.git
   cd inventory-pro
   ```

2. **Create a virtual environment**
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
   # Edit .env with your configuration:
   # - SECRET_KEY=your-secret-key
   # - DEBUG=True
   # - GEMINI_API_KEY=your-gemini-api-key
   ```

5. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Populate with sample data (optional)**
   ```bash
   python manage.py populate_data
   ```

8. **Start the development server**
   ```bash
   python manage.py runserver
   ```

9. **Start Celery worker (for background tasks)**
   ```bash
   # In a separate terminal
   celery -A inventory worker -l info
   ```

### Access the Application

- **Dashboard**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/

---

## 🤖 AI Chat Tools

The AI assistant has access to 20+ specialized tools:

| Category        | Tools                                                                                                                                                                       |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Basic Data**  | `get_categories`, `get_products`, `get_users`, `get_merchants`, `get_representatives`, `get_transactions`, `get_transaction_items`, `get_transaction_types`                 |
| **Statistics**  | `get_inventory_stats`, `get_daily_transactions_summary`, `get_top_products_by_sales`, `get_top_merchants_by_debt`, `get_top_merchants_by_transactions`, `get_today_summary` |
| **Predictions** | `get_low_stock_alert`, `get_stock_predictions`, `get_products_by_category`                                                                                                  |
| **Financial**   | `get_monthly_revenue`, `get_monthly_payments`                                                                                                                               |
| **Search**      | `search_products`, `search_users`, `get_user_transactions`, `get_product_transactions`                                                                                      |

---

## 📝 Environment Variables

| Variable            | Description                           | Required                              |
| ------------------- | ------------------------------------- | ------------------------------------- |
| `SECRET_KEY`        | Django secret key                     | ✅                                     |
| `DEBUG`             | Debug mode (True/False)               | ✅                                     |
| `GEMINI_API_KEY`    | Google Gemini API key for AI features | ✅                                     |
| `CELERY_BROKER_URL` | Redis URL for Celery                  | ❌ (default: redis://localhost:6379/0) |

---

## 🌍 Localization

This application is fully localized for Arabic:

- **Language**: Arabic (ar)
- **Timezone**: Africa/Khartoum
- **Text Direction**: RTL (Right-to-Left)
- **Number Formatting**: Thousand separators enabled
- **Fonts**: Cairo (optimized for Arabic)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📧 Contact

For questions or support, please open an issue on GitHub.

---
