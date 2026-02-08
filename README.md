# Inventory SaaS Platform

A modern, multi-tenant SaaS solution for inventory management and Point of Sale (POS) operations. Built with Django and TailwindCSS.

## 🚀 Features

### Multi-Tenancy
- **Company Isolation**: Complete data separation between tenants.
- **Subscription Plans**: Flexible tiers controlling user limits, product limits, and feature access (POS/Inventory).
- **Role-Based Access**:
  - **Platform Manager**: Superuser who approves companies and manages plans.
  - **Company Manager**: Manages company settings, subscription, and staff.
  - **Accountant**: Manages inventory, categories, and approves rep transactions.
  - **Representative**: Request-based workflow for taking/restoring stock.
  - **Cashier**: Dedicated POS interface for sales.

### Core Modules

#### 🔐 Accounts
- Company registration and approval workflow.
- User management with role assignment.
- Subscription status and renewal tracking.
- Tax configuration (VAT).

#### 📦 Inventory
- Product usage tracking and low stock alerts.
- Transaction approval system (Take / Restore / Payment).
- Representative custody tracking.
- Category management.

#### 🛒 Point of Sale (POS)
- Fast checkout interface with barcode support.
- Cart holding/clearing.
- Receipt printing (80mm thermal format).
- Daily sales summary.
- Cash/Card/Split payment support.

## 🛠️ Technology Stack
- **Backend**: Python 3, Django 4.2
- **Database**: SQLite (Dev) / PostgreSQL (Prod recommended)
- **Frontend**: Django Templates, TailwindCSS, DaisyUI (via CDN)
- **PDF/Printing**: Native browser print support

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd inventory-saas
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Setup**
   ```bash
   # Remove old db if exists (optional reset)
   rm db.sqlite3
   
   # Run migrations
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create Platform Manager**
   ```bash
   python manage.py createsuperuser
   # Login to admin at /admin/ or platform dashboard at /accounts/platform/
   ```

5. **Run Server**
   ```bash
   python manage.py runserver
   ```

## 👥 Usage Guide

### Getting Started
1. **Register a Company**: Go to `/accounts/register/` and sign up.
2. **Approve Company**: Login as Platform Manager -> Dashboard -> Click "Activate" on the new company.
3. **Setup Company**: Login as Company Manager -> Add staff (Accountant, Cashier, etc.).

### Roles & Responsibilities
- **Accountant**: Log in to access the Inventory Dashboard. Add products, categories, and manage rep requests.
- **Representative**: Log in to the Representative Portal to request stock or submit payments.
- **Cashier**: Log in to the POS interface to process sales.

## 📝 License
Proprietary software. All rights reserved.
